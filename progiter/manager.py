r"""
Progress Manager
----------------

This is watch.utils.manager ported from geowatch.

CommandLine:
    DEMO_PROGRESS=1 xdoctest -m progiter.manager __doc__

Example:
    >>> # xdoctest: +REQUIRES(env:DEMO_PROGRESS)
    >>> print('First a simple example')
    >>> from progiter.manager import ProgressManager
    >>> import time
    >>> iterable = range(1000)
    >>> pman = ProgressManager()
    >>> with pman:
    >>>     for item in pman.progiter(iterable, desc='big loop'):
    >>>         time.sleep(0.005)


Example:
    >>> # xdoctest: +REQUIRES(env:DEMO_PROGRESS)
    >>> print('Choose your backend!')
    >>> from progiter.manager import ProgressManager
    >>> import time
    >>> iterable = range(1000)
    >>> print('threaded rich backend')
    >>> pman = ProgressManager(backend='rich')
    >>> with pman:
    >>>     for item in pman.progiter(iterable, desc='big loop'):
    >>>         time.sleep(0.005)
    >>> ...
    >>> print('unthreaded progiter backend')
    >>> pman = ProgressManager(backend='progiter')
    >>> with pman:
    >>>     for item in pman.progiter(iterable, desc='big loop'):
    >>>         time.sleep(0.005)

Example:
    >>> # xdoctest: +REQUIRES(env:DEMO_PROGRESS)
    >>> print('Now a more complex example')
    >>> from progiter.manager import ProgressManager
    >>> import time
    >>> delay = 0.01
    >>> # Can use plain progiter or rich
    >>> # The usecase for plain progiter is when threads / live output
    >>> # is not desirable and you just want plain stdout progress
    >>> for backend in ['rich', 'progiter']:
    >>>     print(f'\n\n -- starting {backend} --\n\n')
    >>>     pman = ProgressManager(backend=backend)
    >>>     with pman:
    >>>         pbar1 = pman.progiter(range(5), desc='outer loop', verbose=3)
    >>>         for i in pbar1:
    >>>             pbar1.set_postfix(f'\\[step {i}]', refresh=False)
    >>>             for j1 in pman.progiter(range(100), desc=f'prepare inner loop {i}', transient=True):
    >>>                 time.sleep(delay / 3)
    >>>             for j2 in pman.progiter(range(100), desc=f'execute inner loop {i}'):
    >>>                 time.sleep(delay)
    >>>             for j3 in pman.progiter(range(100), desc=f'shutdown inner loop {i}', transient=True):
    >>>                 time.sleep(delay / 3)
"""
from __future__ import annotations

import contextvars
import importlib.util
import os
import sys
import time
import weakref
from types import TracebackType
from typing import Any, Iterable, Iterator, Type

from progiter.progiter import ProgIter


__all__ = ['ProgressManager']


def _coerce_envflag(value: Any) -> bool:
    """
    Coerce common environment variable truthy / falsy strings.

    Example:
        >>> from progiter.manager import _coerce_envflag
        >>> assert _coerce_envflag('1') is True
        >>> assert _coerce_envflag('true') is True
        >>> assert _coerce_envflag('0') is False
        >>> assert _coerce_envflag('false') is False
        >>> assert _coerce_envflag('') is False
        >>> assert _coerce_envflag('unexpected') is True
    """
    value = str(value).strip().lower()
    if value in {'', '0', 'false', 'no', 'off'}:
        return False
    if value in {'1', 'true', 'yes', 'on'}:
        return True
    return bool(value)


def _coerce_choice(value: Any, choices: set[str], name: str) -> str:
    """Validate a small string-valued policy."""
    value = str(value).strip().lower()
    if value not in choices:
        raise KeyError(f'{name}={value!r} must be one of {sorted(choices)!r}')
    return value


def _rich_is_available() -> bool:
    """
    Check whether rich is importable without importing it.

    Example:
        >>> from progiter.manager import _rich_is_available
        >>> assert isinstance(_rich_is_available(), bool)
    """
    return importlib.util.find_spec('rich') is not None


def _detect_notebook() -> bool:
    """
    Best-effort notebook detection used only by backend='auto'.

    Example:
        >>> from progiter.manager import _detect_notebook
        >>> assert isinstance(_detect_notebook(), bool)
    """
    try:
        builtins_obj: Any = __builtins__
        get_ipython = builtins_obj.get('get_ipython')
    except AttributeError:
        get_ipython = getattr(__builtins__, 'get_ipython', None)
    if get_ipython is None:
        return False
    try:
        shell = get_ipython()
    except Exception:
        return False
    if shell is None:
        return False
    shell_name = shell.__class__.__name__
    return shell_name in {'ZMQInteractiveShell', 'Shell'}


def _stream_is_tty(stream: Any = None) -> bool:
    """
    Check if a stream appears to be interactive.

    Example:
        >>> from progiter.manager import _stream_is_tty
        >>> assert isinstance(_stream_is_tty(None), bool)
    """
    if stream is None:
        stream = getattr(sys, 'stderr', None)
    isatty = getattr(stream, 'isatty', None)
    if isatty is None:
        return False
    try:
        return bool(isatty())
    except Exception:
        return False


# If truthy disable all threaded rich options
# In backend='auto' this now means avoiding threaded rich options
PROGITER_NOTHREAD: bool | str = os.environ.get('PROGITER_NOTHREAD', 'auto')
if str(PROGITER_NOTHREAD).strip().lower() == 'auto':
    # Use rich outside of slurm
    PROGITER_NOTHREAD = bool(os.environ.get('SLURM_JOBID', ''))
else:
    PROGITER_NOTHREAD = _coerce_envflag(PROGITER_NOTHREAD)


LIVE_PROGRESS_MANAGERS: weakref.WeakValueDictionary[int, Any] = weakref.WeakValueDictionary()
_RICH_MANAGER_STACKVAR: contextvars.ContextVar[tuple[Any, ...]] = contextvars.ContextVar('progiter_rich_manager_stack', default=())


def _get_rich_manager_stack() -> tuple[Any, ...]:
    return _RICH_MANAGER_STACKVAR.get()


def _get_current_rich_manager() -> Any | None:
    """
    Return the current active rich manager for this context.

    Example:
        >>> from progiter.manager import _get_current_rich_manager
        >>> assert _get_current_rich_manager() is None
    """
    for manager in reversed(_get_rich_manager_stack()):
        try:
            if manager.enabled and manager._active:
                return manager
        except ReferenceError:
            ...
    return None


def _push_current_rich_manager(manager: Any) -> None:
    stack = tuple(m for m in _get_rich_manager_stack() if m is not manager)
    _RICH_MANAGER_STACKVAR.set(stack + (manager,))


def _pop_current_rich_manager(manager: Any) -> None:
    stack = tuple(m for m in _get_rich_manager_stack() if m is not manager)
    _RICH_MANAGER_STACKVAR.set(stack)


def _normalize_progkw(default_progkw: dict[str, Any], verbose: Any, kw: dict[str, Any]) -> dict[str, Any]:
    """
    Merge manager defaults with per-progress keyword arguments.

    Example:
        >>> from progiter.manager import _normalize_progkw
        >>> result = _normalize_progkw({'verbose': 2, 'freq': 10}, 'auto', {'freq': 3})
        >>> assert result['verbose'] == 2
        >>> assert result['freq'] == 3
        >>> result = _normalize_progkw({'verbose': 2}, 0, {})
        >>> assert result['verbose'] == 0
    """
    progkw = default_progkw.copy()
    progkw.update(kw)
    progkw['verbose'] = verbose
    if verbose == 'auto':
        progkw['verbose'] = default_progkw.get('verbose', 1)
    return progkw


def _choose_auto_backend(auto_policy: str = 'auto', stream: Any = None, enabled: bool = True) -> str:
    """
    Choose a backend for ``backend='auto'``.

    Example:
        >>> from progiter.manager import _choose_auto_backend
        >>> assert _choose_auto_backend(enabled=False) == 'none'
        >>> assert _choose_auto_backend(auto_policy='progiter') == 'progiter'
        >>> assert _choose_auto_backend(auto_policy='tty', stream=object()) == 'progiter'
    """
    auto_policy = _coerce_choice(auto_policy, {'auto', 'rich', 'progiter', 'tty', 'notebook'}, 'auto_policy')
    if not enabled:
        return 'none'
    if PROGITER_NOTHREAD:
        return 'progiter'
    if auto_policy == 'progiter':
        return 'progiter'
    rich_available = _rich_is_available()
    if auto_policy == 'rich':
        return 'rich' if rich_available else 'progiter'
    if auto_policy == 'tty':
        return 'rich' if rich_available and _stream_is_tty(stream) else 'progiter'
    if auto_policy == 'notebook':
        return 'rich' if rich_available and _detect_notebook() else 'progiter'
    return 'rich' if rich_available else 'progiter'


class ManagedProgIter(ProgIter):
    """
    Simple subclass of ProgIter to allowed it to be managed.
    """

    info_text: Any
    manager: Any


    def _set_manager(self, manager: Any) -> None:
        self.manager = weakref.proxy(manager)

    def update_info(self, text: Any) -> None:
        if not self.enabled:
            return None
        self.info_text = text
        info_text = getattr(self, 'info_text', None)
        self.ensure_newline()
        if info_text is not None:
            # if self._cursor_at_newline:
            print('+ --- Info --- +')
            print(info_text)
            print('+ ------------ +')
        # self.display_message()
        return None

    def update(self, n: int = 1) -> None:
        if not self.started:
            self.begin()
        manager = getattr(self, 'manager', None)
        if manager is not None:
            # TODO: vet this, not quite working. The idea is if part of a
            # progress manager and this is not the "tail" progiter (i.e. it
            # isn't the only progiter allowed to be clearing newlines) then we
            # should ensure that the progiter that is allowed to clear the
            # newline has its ensure_newline method called so we can actually
            # write our progress without getting clobbered. The ReferenceError
            # handling below only protects against a stale weak manager proxy;
            # it does not prove this tail-progiter newline policy is correct.
            try:
                if len(manager.prog_iters) and manager.prog_iters[-1] is not self:
                    manager.prog_iters[-1].ensure_newline()
            except ReferenceError:
                ...
        super().update(n=n)

    def end(self) -> Any:
        try:
            ret = super().end()
        finally:
            manager = getattr(self, 'manager', None)
            if manager is not None:
                try:
                    manager._deregister_progiter(self)
                except ReferenceError:
                    ...
                except AttributeError:
                    ...
        return ret

    def display_message(self) -> None:
        super().display_message()


class RichProgIter:
    """
    Ducktypes ManagedProgIter

    TODO: enhance with the ability to have a update info panel that removes
    the circular reference

    Ignore:
        from progiter import manager
        manager.LIVE_PROGRESS_MANAGERS
        print(len(manager.LIVE_PROGRESS_MANAGERS))

        for v in manager.LIVE_PROGRESS_MANAGERS.values():
            ...

        from progiter import *  # NOQA
        for _ in RichProgIter(range(1000)):
            ...

    Example:
        >>> # xdoctest: +REQUIRES(module:rich)
        >>> from progiter.manager import ProgressManager
        >>> pman = ProgressManager(backend='rich')
        >>> prog = pman.progiter(iter(range(3)), total=None, unknown_total_policy='complete')
        >>> assert prog.unknown_total_policy == 'complete'
        >>> assert list(prog) == [0, 1, 2]
        >>> assert prog._completed == 3
        >>> assert pman.backend._active is False

    """

    manager: Any
    iterable: Any
    enabled: bool
    spinner: bool
    total: int | None
    desc: Any | None
    task_id: Any
    transient: bool
    extra: Any | None
    initial: int
    started: bool
    finished: bool
    freq: int
    time_thresh: float | None
    unknown_total_policy: str
    refresh_policy: str


    def __init__(self, iterable: Any = None, desc: Any | None = None,
                 total: int | None = None, freq: int = 1, initial: int = 0,
                 eta_window: int = 64, clearline: bool = True, adjust: bool = True,
                 time_thresh: float | None = 2.0, show_times: bool = True,
                 show_wall: bool = False, enabled: bool = True,
                 verbose: Any | None = None, stream: Any | None = None,
                 chunksize: Any | None = None, rel_adjust_limit: float = 4.0,
                 transient: bool = False, manager: Any | None = None,
                 spinner: bool = False, unknown_total_policy: str = 'complete',
                 refresh_policy: str = 'auto', _self_managed: bool = False,
                 **kwargs: Any) -> None:

        unhandled = {
            'eta_window', 'clearline', 'adjust', 'time_thresh', 'show_times',
            'show_wall', 'stream', 'chunksize', 'rel_adjust_limit',
        }
        # kwargs = udict(kwargs) - unhandled
        kwargs = {k: v for k, v in kwargs.items() if k not in unhandled}

        if manager is None:
            manager = _RichProgIterManager()
            self._self_managed = True
        else:
            manager = weakref.proxy(manager)
            self._self_managed = bool(_self_managed)

        if verbose is None:
            verbose = 1

        if not verbose:
            enabled = False

        self.manager = manager
        self.iterable = iterable
        self.enabled = enabled
        self.spinner = spinner
        if total is None:
            try:
                total = len(iterable)
            except Exception:
                ...
        self.total = total
        self.desc = desc
        self.initial = initial
        self.transient = transient
        self.extra = None
        self.started = False
        self.finished = False
        self._removed = False
        self._completed = initial
        self._displayed_completed = initial
        self._pending_advance = 0
        self._last_flush_time = time.monotonic()
        self.freq = max(int(freq or 1), 1)
        self.time_thresh = time_thresh
        if self.time_thresh is not None:
            self.time_thresh = max(float(self.time_thresh), 0.0)
        self.unknown_total_policy = _coerce_choice(
            unknown_total_policy, {'complete', 'keep'}, 'unknown_total_policy')
        self.refresh_policy = _coerce_choice(
            'throttle' if refresh_policy == 'auto' else refresh_policy,
            {'throttle', 'eager', 'manual'}, 'refresh_policy')

        addtask_kw = {}
        if desc is not None:
            addtask_kw['description'] = desc
        else:
            addtask_kw['description'] = ''
        addtask_kw['total'] = self.total
        if initial:
            addtask_kw['completed'] = initial

        if self.enabled:
            self.task_id = self.manager.rich_progress.add_task(**addtask_kw)
        else:
            self.task_id = None

    def start(self) -> Any:
        return self.begin()

    def stop(self) -> Any:
        return self.end()

    def begin(self) -> Any:
        if not self.started:
            if self._self_managed:
                self.manager.start()
            self.started = True
        return self

    def _should_flush(self, force: bool = False) -> bool:
        if force:
            return True
        if self.refresh_policy == 'manual':
            return False
        if self.refresh_policy == 'eager':
            return True
        if self._pending_advance < self.freq:
            return False
        if self.time_thresh is None:
            return True
        return (time.monotonic() - self._last_flush_time) >= self.time_thresh

    def _flush(self, force: bool = False, refresh: bool = False) -> None:
        if not self.enabled or self._removed or not self._pending_advance:
            return None
        if not self._should_flush(force=force):
            return None
        advance = self._pending_advance
        self._pending_advance = 0
        self._displayed_completed += advance
        self._last_flush_time = time.monotonic()
        self.manager.rich_progress.update(
            self.task_id, advance=advance, refresh=bool(refresh or force))
        return None

    def _finalize_unknown_total(self) -> None:
        if not self.enabled or self._removed or self.total is not None:
            return None
        if self.unknown_total_policy == 'complete':
            self.manager.rich_progress.update(
                self.task_id, total=self._completed, completed=self._completed)
        return None

    def end(self) -> Any:
        if not self.finished:
            self._flush(force=True, refresh=True)
            if not self.transient:
                self._finalize_unknown_total()
            if self.transient:
                self.remove()
            self.finished = True
            try:
                self.manager._deregister_progiter(self)
            except ReferenceError:
                ...
            except AttributeError:
                ...
        if self._self_managed:
            try:
                self.manager.stop()
            except ReferenceError:
                ...
        return self

    def update(self, n: int = 1) -> None:
        if not self.started:
            self.begin()
        self._completed += n
        self._pending_advance += n
        self._flush()
        return None

    step = update

    def __iter__(self) -> Iterator[Any]:
        if not self.enabled:
            self.begin()
            try:
                yield from self.iterable
            finally:
                self.end()
        else:
            self.start()
            try:
                for item in self.iterable:
                    yield item
                    self.update(1)
            finally:
                self.stop()

    def remove(self) -> None:
        """
        Remove this progress task from its rich manager
        """
        if self.enabled and not self._removed:
            self._flush(force=True, refresh=True)
            self.manager.rich_progress.remove_task(self.task_id)
            self._removed = True
        return None

    def update_info(self, text: Any) -> None:
        if self.enabled:
            # FIXME: remove circular reference
            try:
                self.manager.update_info(text)
            except ReferenceError:
                ...
        return None

    def ensure_newline(self) -> None:
        ...

    def set_postfix_str(self, text: str, refresh: bool = True) -> None:
        self.extra = text
        parts = [self.desc] if self.desc is not None else []
        if self.extra is not None:
            parts.append(self.extra)
        if self.enabled and not self._removed:
            description = ' '.join(parts)
            self._flush(force=refresh, refresh=refresh)
            self.manager.rich_progress.update(
                self.task_id, description=description, refresh=refresh)
        return None

    set_postfix = set_postfix_str
    set_extra = set_postfix_str


class BaseProgIterManager:
    def new(self, *args: Any, **kw: Any) -> Any:
        return getattr(self, 'progiter')(*args, **kw)

    def __call__(self, *args: Any, **kw: Any) -> Any:
        return getattr(self, 'progiter')(*args, **kw)

    def start(self) -> Any:
        return self

    def begin(self) -> Any:
        return self.start()

    def stop(self, **kwargs: Any) -> Any:
        ...

    def __enter__(self) -> Any:
        return self.start()

    def __exit__(self, exc_type: Type[BaseException] | None = None, exc_val: BaseException | None = None, exc_tb: TracebackType | None = None) -> Any:
        return self.stop(exc_type=exc_type, exc_val=exc_val, exc_tb=exc_tb)




class _RichProgIterManager(BaseProgIterManager):
    """
    rich specific backend.

    Example:
        >>> # xdoctest: +REQUIRES(module:rich)
        >>> # Test verbose = 0
        >>> from progiter.manager import ProgressManager
        >>> import time
        >>> pman = ProgressManager(backend='rich', verbose=0)
        >>> with pman:
        >>>     for i in pman.progiter(range(10), desc='should not show1'):
        >>>         ...
        >>>     for i in pman.progiter(range(10), verbose=1, desc='should show2'):
        >>>         ...
        >>>     for i in pman.progiter(range(10), verbose=0, desc='should not show3'):
        >>>         ...
    """

    prog_iters: list[Any]
    enabled: bool
    info_panel: Any
    rich_progress: Any
    default_progkw: dict[str, Any]
    live_context: Any
    progress_group: Any
    _is_main_manager: Any


    def __init__(self, **kwargs: Any) -> None:
        self.prog_iters = []
        self.enabled = kwargs.pop('enabled', True)
        self.info_panel = None
        self.rich_progress = None
        self.progress_group = None
        self.live_context = None
        self._is_main_manager = None

        self.setup_rich()
        self._active = False
        self._stacked = False

        self.default_progkw = dict({
            'verbose': kwargs.pop('verbose', 1),
            'unknown_total_policy': kwargs.pop('unknown_total_policy', 'complete'),
            'refresh_policy': kwargs.pop('refresh_policy', 'auto'),
        })
        self.default_progkw.update(kwargs)

    # Can we make this work?
    # def __del__(self):
    #     if self._active:
    #         self.stop()

    def _deregister_progiter(self, prog: Any) -> None:
        self.prog_iters = [p for p in self.prog_iters if p is not prog and not p.finished]

    def _ensure_attached(self) -> None:
        if self.rich_progress is None:
            self.setup_rich()
        elif not self._is_main_manager and not self._active and _get_current_rich_manager() is None:
            self.setup_rich()

    def progiter(self, iterable: Iterable[Any] | None = None, total: int | None = None,
                 desc: Any | None = None, transient: bool = False,
                 spinner: bool = False, verbose: Any = 'auto', **kw: Any) -> Any:
        self._ensure_attached()
        # Fixme remove circular ref
        # Historical note: keep avoiding assignment onto rich_progress.pman;
        # ownership now stays on the manager / progiter objects.
        # self.rich_progress.pman = self
        was_active = self._active
        if not was_active:
            self.start()
        self.prog_iters = [p for p in self.prog_iters if not p.finished]
        progkw = _normalize_progkw(self.default_progkw, verbose, kw)
        prog = RichProgIter(
            manager=self, iterable=iterable, total=total, desc=desc,
            transient=transient, spinner=spinner,
            _self_managed=not was_active, **progkw)
        self.prog_iters.append(prog)
        return prog

    def setup_rich(self) -> None:
        rich = __import__('rich')
        rich_progress_mod = __import__('rich.progress', fromlist=[''])
        rich_console_mod = __import__('rich.console', fromlist=[''])
        rich_live_mod = __import__('rich.live', fromlist=[''])

        Group = rich_console_mod.Group
        Live = rich_live_mod.Live
        BarColumn = rich_progress_mod.BarColumn
        TextColumn = rich_progress_mod.TextColumn
        richProgress = rich_progress_mod.Progress
        SpinnerColumn = rich_progress_mod.SpinnerColumn
        ProgressColumnBase: Any = rich_progress_mod.ProgressColumn
        Text = rich_progress_mod.Text
        # from rich.style import Style

        current = _get_current_rich_manager()
        if current is not None and current is not self:
            self._is_main_manager = False
            self.live_context = None
            self.rich_progress = current.rich_progress
            self.progress_group = current.progress_group
            self.info_panel = current.info_panel
        else:
            self._is_main_manager = True

            class ProgressRateColumn(ProgressColumnBase):
                """Renders human readable transfer speed."""

                def render(self, task: Any) -> Any:
                    """Show progress speed speed."""
                    _iters_per_second = task.finished_speed or task.speed
                    if _iters_per_second is not None:
                        rate_format = '4.2f' if _iters_per_second > .001 else 'g'
                        fmt = '{:' + rate_format + '} Hz'
                        text = fmt.format(_iters_per_second)
                    else:
                        text = '?'
                    # style = Style(color="red")
                    style = 'progress.data.speed'
                    renderable = Text(text, style=style)
                    return renderable

            self.rich_progress = richProgress(
                TextColumn("{task.description}"),
                SpinnerColumn(),
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.0f}%",
                rich_progress_mod.MofNCompleteColumn(),
                # rich.progress.TransferSpeedColumn(),
                ProgressRateColumn(),
                'eta',
                rich_progress_mod.TimeRemainingColumn(),
                'total',
                rich_progress_mod.TimeElapsedColumn(),
            )
            self.info_panel = None
            self.progress_group = Group(
                # self.info_panel,
                self.rich_progress,
            )
            self.live_context = Live(self.progress_group)

    def update_info(self, text: Any) -> None:
        if self.enabled:
            self._ensure_attached()
            if not self._is_main_manager:
                current = _get_current_rich_manager()
                if current is not None and current is not self:
                    return current.update_info(text)
            Panel = __import__('rich.panel', fromlist=['']).Panel
            if self.info_panel is None:
                self.info_panel = Panel(text)
                self.progress_group.renderables.insert(0, self.info_panel)
            else:
                self.info_panel.renderable = text
        return None

    def start(self) -> Any:
        if self.enabled and not self._active:
            self._ensure_attached()
            if self._is_main_manager:
                self.live_context.__enter__()
                _push_current_rich_manager(self)
                self._stacked = True
            self._active = True
        return self

    def stop(self, **kw: Any) -> Any:
        ret = None
        if self.enabled and self._active:
            if not kw:
                kw = {'exc_type': None, 'exc_val': None, 'exc_tb': None}
            if self._is_main_manager:
                try:
                    ret = self.live_context.__exit__(**kw)
                finally:
                    if self._stacked:
                        _pop_current_rich_manager(self)
                        self._stacked = False
            self._active = False
        return ret


class _ProgIterManager(BaseProgIterManager):
    """
    progiter specific backend
    """

    enabled: bool
    default_progkw: dict[str, Any]
    prog_iters: list[ManagedProgIter]


    _is_main_manager = False

    def __init__(self, **kwargs: Any) -> None:
        self.enabled = kwargs.get('enabled', True)
        # Default arguments for new progiters
        self.default_progkw = {
            'time_thresh': 2.0,
        }
        self.default_progkw.update(kwargs)
        self.prog_iters = []
        self._active = False

    def _deregister_progiter(self, prog: Any) -> None:
        self.prog_iters = [p for p in self.prog_iters if p is not prog and not p.finished]

    def progiter(self, iterable: Iterable[Any] | None = None, total: int | None = None,
                 desc: Any | None = None, transient: bool = False,
                 spinner: bool = False, verbose: Any = 'auto', **kw: Any) -> Any:
        progkw = _normalize_progkw(self.default_progkw, verbose, kw)
        self.prog_iters = [p for p in self.prog_iters if not p.finished]
        if True:
            # Change all other - now outer - progiters to verbose=3 mode
            for other in self.prog_iters:
                other.ensure_newline()
                if other.enabled:
                    other.clearline = False
                    other.adjust = False
                    other.freq = 1
        prog = ManagedProgIter(iterable, total=total, desc=desc, **progkw)
        prog._set_manager(self)
        self.prog_iters.append(prog)
        return prog

    def update_info(self, text: Any) -> None:
        if self.enabled:
            self.prog_iters = [p for p in self.prog_iters if not p.finished]
            if len(self.prog_iters) == 0:
                # if self._cursor_at_newline:
                print('+ --- Info --- +')
                print(text)
                print('+ ------------ +')
            else:
                self.prog_iters[0].update_info(text)
        return None


class ProgressManager(BaseProgIterManager):
    r"""
    A progress manager.

    Manage multiple progress bars, either with rich or ProgIter.

    CommandLine:
        xdoctest -m progiter.manager ProgressManager:0
        xdoctest -m progiter.manager ProgressManager:1
        xdoctest -m progiter.manager ProgressManager:2

    Example:
        >>> from progiter.manager import ProgressManager
        >>> from progiter import progiter
        >>> # Can use plain progiter or rich
        >>> # The usecase for plain progiter is when threads / live output
        >>> # is not desirable and you just want plain stdout progress
        >>> pman = ProgressManager(backend='progiter')
        >>> with pman:
        >>>     oprog = pman.progiter(range(20), desc='outer loop', verbose=3)
        >>>     for i in oprog:
        >>>         oprog.set_postfix(f'Doing step {i}', refresh=False)
        >>>         for i in pman.progiter(range(100), desc=f'inner loop {i}'):
        >>>             pass
        >>> #
        >>> # xdoctest: +REQUIRES(module:rich)
        >>> self = pman = ProgressManager(backend='rich')
        >>> pman = ProgressManager(backend='rich')
        >>> with pman:
        >>>     oprog = pman.progiter(range(20), desc='outer loop', verbose=3)
        >>>     for i in oprog:
        >>>         oprog.set_postfix(f'Doing step {i}', refresh=False)
        >>>         for i in pman.progiter(range(100), desc=f'inner loop {i}'):
        >>>             pass

    Example:
        >>> # A fairly complex example
        >>> # xdoctest: +REQUIRES(module:rich)
        >>> from progiter.manager import ProgressManager
        >>> import time
        >>> delay = 0.00005
        >>> N_inner = 300
        >>> N_outer = 11
        >>> self = pman = ProgressManager(backend='rich')
        >>> with pman:
        >>>     oprog = pman(range(N_outer), desc='outer loop')
        >>>     for i in oprog:
        >>>         if i > 7:
        >>>             self.update_info(f'The info panel gives detailed updates\nWe are now at step {i}\nWe are just about done now')
        >>>         elif i > 5:
        >>>             self.update_info(f'The info panel gives detailed updates\nWe are now at step {i}')
        >>>         oprog.set_postfix(f'Doing step {i}')
        >>>         N = 1000
        >>>         for j in pman(iter(range(N_inner)), total=None if i % 2 == 0 else N_inner, desc=f'inner loop {i}', transient=i < 4):
        >>>             time.sleep(delay)

    Example:
        >>> # Test complex example over a grid of parameters
        >>> # xdoctest: +REQUIRES(module:ubelt)
        >>> # xdoctest: +REQUIRES(module:rich)
        >>> import ubelt as ub
        >>> from progiter.manager import ProgressManager, ManagedProgIter
        >>> import time
        >>> delay = 0.000005
        >>> N_inner = 300
        >>> N_outer = 11
        >>> basis = {
        >>>     'with_info': [0, 1],
        >>>     'backend': ['progiter', 'rich'],
        >>>     'enabled': [0, 1],
        >>>     #'with_info': [1],
        >>> }
        >>> grid = list(ub.named_product(basis))
        >>> grid_prog = ManagedProgIter(grid, desc='Test cases over grid', verbose=3)
        >>> grid_prog.update_info('Here we go')
        >>> for item in grid:
        >>>     grid_prog.ensure_newline()
        >>>     grid_prog.update_info(f'Running grid test {ub.urepr(item, nl=1)}')
        >>>     print('\n\n')
        >>>     self = ProgressManager(backend=item['backend'], enabled=item['enabled'])
        >>>     with self:
        >>>         outer_prog = self.progiter(range(N_outer), desc='outer loop')
        >>>         for i in outer_prog:
        >>>             if item['with_info']:
        >>>                 if i > 7:
        >>>                     outer_prog.update_info(f'The info panel gives detailed updates\nWe are now at step {i}\nWe are just about done now')
        >>>                 elif i > 5:
        >>>                     outer_prog.update_info(f'The info panel gives detailed updates\nWe are now at step {i}')
        >>>             outer_prog.set_postfix(f'Doing step {i}')
        >>>             inner_kwargs = dict(
        >>>                 total=None if i % 2 == 0 else N_inner,
        >>>                 transient=i < 4,
        >>>                 time_thresh=delay * 2.3,
        >>>                 desc=f'inner loop {i}',
        >>>             )
        >>>             for j in self.progiter(iter(range(N_inner)), **inner_kwargs):
        >>>                 time.sleep(delay)
        >>>     grid_prog.update_info(f'Finished test item')

    Example:
        >>> # Demo manual usage
        >>> # xdoctest: +REQUIRES(module:rich)
        >>> from progiter.manager import ProgressManager
        >>> from progiter import manager
        >>> import time
        >>> pman = ProgressManager()
        >>> pman.start()
        >>> task1 = pman.progiter(desc='task1', total=100)
        >>> task2 = pman.progiter(desc='task2')
        >>> for i in range(100):
        >>>     task1.update()
        >>>     task2.update(2)
        >>>     time.sleep(0.001)
        >>> ProgressManager.stopall()

    Example:
        >>> # Demo manual usage (progiter backend)
        >>> from progiter.manager import ProgressManager
        >>> from progiter import manager
        >>> import time
        >>> pman = ProgressManager(backend='progiter', adjust=0, freq=1)
        >>> pman.start()
        >>> task1 = pman.progiter(desc='task1', total=12)
        >>> task2 = pman.progiter(desc='task2')
        >>> task1.update()
        >>> task2.update()
        >>> for i in range(10):
        >>>     time.sleep(0.001)
        >>>     task1.update()
        >>>     time.sleep(0.001)
        >>>     task2.update(2)
        >>> ProgressManager.stopall()

    Example:
        >>> # backend='auto' is where fallback and display policy live.
        >>> from progiter.manager import ProgressManager
        >>> pman = ProgressManager(backend='auto', auto_policy='progiter')
        >>> assert pman.backend_key == 'progiter'
        >>> pman = ProgressManager(backend='auto', enabled=False)
        >>> assert pman.backend_key == 'none'
        >>> assert list(pman.progiter(range(3))) == [0, 1, 2]

    Example:
        >>> # xdoctest: +REQUIRES(module:rich)
        >>> from progiter.manager import ProgressManager
        >>> pman = ProgressManager(backend='rich', unknown_total_policy='keep')
        >>> assert pman.backend_key == 'rich'
        >>> prog = pman.progiter(iter(range(2)), total=None, verbose=0)
        >>> assert prog.unknown_total_policy == 'keep'

    """

    backend: Any
    backend_key: str
    requested_backend: str
    auto_policy: str


    def __init__(self, backend: str = 'auto', **kwargs: Any) -> None:
        LIVE_PROGRESS_MANAGERS[id(self)] = self
        auto_policy = kwargs.pop('auto_policy', 'auto')
        enabled = kwargs.get('enabled', True)
        stream = kwargs.get('stream', None)
        requested_backend = backend

        # TODO: check if we are being tee-d and use progiter instead if we are.
        # Historical note: backend='auto' now has auto_policy='tty' for callers
        # that want TTY detection, but the default auto policy still does not
        # force tee detection.
        if backend == 'auto':
            backend = _choose_auto_backend(
                auto_policy=auto_policy, stream=stream, enabled=enabled)
        else:
            backend = _coerce_choice(backend, {'rich', 'progiter', 'none'}, 'backend')

        if backend == 'none':
            self.backend = _NullProgIterManager(**kwargs)
        elif backend == 'rich':
            self.backend = _RichProgIterManager(**kwargs)
        elif backend == 'progiter':
            if not enabled:
                self.backend = _NullProgIterManager(**kwargs)
                backend = 'none'
            else:
                self.backend = _ProgIterManager(**kwargs)
        else:
            raise KeyError(backend)

        self.backend_key = backend
        self.requested_backend = requested_backend
        self.auto_policy = auto_policy

    def progiter(self, *args: Any, **kw: Any) -> Any:
        return self.backend.progiter(*args, **kw)

    def update_info(self, text: Any) -> None:
        return self.backend.update_info(text)

    def start(self) -> Any:
        self.backend.start()
        return self

    def stop(self, *args: Any, **kwargs: Any) -> Any:
        return self.backend.stop(*args, **kwargs)

    @property
    def _is_main_manager(self) -> bool:
        return bool(getattr(self.backend, '_is_main_manager', False))

    @classmethod
    def stopall(cls, backend: str | None = None, raise_errors: bool = False) -> list[Exception]:
        """
        Stop all live progress managers.

        Args:
            backend (str | None): If specified, only stop managers whose
                resolved backend matches this value.
            raise_errors (bool): If True, re-raise the first cleanup error.

        Returns:
            list[Exception]: cleanup errors, if any.

        Example:
            >>> from progiter import manager
            >>> errors = manager.ProgressManager.stopall()
            >>> assert isinstance(errors, list)
        """
        errors: list[Exception] = []
        for pman in reversed(list(LIVE_PROGRESS_MANAGERS.values())):
            if backend is not None and getattr(pman, 'backend_key', None) != backend:
                continue
            try:
                pman.stop()
            except Exception as ex:
                errors.append(ex)
                if raise_errors:
                    raise
        return errors


class _NullProgIterManager(BaseProgIterManager):
    """
    Disabled backend that avoids output and backend imports.

    Example:
        >>> from progiter.manager import ProgressManager
        >>> pman = ProgressManager(backend='auto', enabled=False)
        >>> assert pman.backend_key == 'none'
        >>> assert list(pman.progiter(range(3))) == [0, 1, 2]
        >>> assert pman.update_info('ignored') is None
    """

    enabled: bool
    default_progkw: dict[str, Any]
    prog_iters: list[Any]
    _is_main_manager: Any


    enabled = False
    _is_main_manager = False

    def __init__(self, **kwargs: Any) -> None:
        self.default_progkw = kwargs.copy()
        self.prog_iters = []
        self._active = False

    def progiter(self, iterable: Iterable[Any] | None = None, total: int | None = None,
                 desc: Any | None = None, transient: bool = False,
                 spinner: bool = False, verbose: Any = 'auto', **kw: Any) -> Any:
        progkw = _normalize_progkw(self.default_progkw, verbose, kw)
        prog = _NullProgIter(
            iterable=iterable, total=total, desc=desc, transient=transient,
            spinner=spinner, manager=self, **progkw)
        return prog

    def update_info(self, text: Any) -> None:
        return None

    def _deregister_progiter(self, prog: Any) -> None:
        return None


class _NullProgIter:
    """
    Cheap no-op progress iterator used when a manager is disabled.

    Example:
        >>> from progiter.manager import _NullProgIter
        >>> prog = _NullProgIter(range(3))
        >>> assert list(prog) == [0, 1, 2]
        >>> assert prog.finished is True
        >>> assert prog.update_info('ignored') is None
    """

    iterable: Any
    desc: Any | None
    total: int | None
    initial: int
    transient: bool
    manager: Any | None
    spinner: bool
    enabled: bool
    started: bool
    finished: bool
    extra: Any | None


    def __init__(self, iterable: Any = None, desc: Any | None = None,
                 total: int | None = None, initial: int = 0,
                 transient: bool = False, manager: Any | None = None,
                 spinner: bool = False, **kwargs: Any) -> None:
        self.iterable = () if iterable is None else iterable
        self.desc = desc
        if total is None and iterable is not None:
            try:
                total = len(iterable)
            except Exception:
                total = None
        self.total = total
        self.initial = initial
        self._completed = initial
        self.transient = transient
        self.manager = manager
        self.spinner = spinner
        self.enabled = False
        self.started = False
        self.finished = False
        self.extra = None

    def __iter__(self) -> Iterator[Any]:
        self.begin()
        try:
            for item in self.iterable:
                yield item
        finally:
            self.end()

    def begin(self) -> Any:
        self.started = True
        return self

    start = begin

    def end(self) -> Any:
        self.finished = True
        return self

    stop = end

    def update(self, n: int = 1) -> None:
        self.begin()
        self._completed += n
        return None

    step = update

    def remove(self) -> None:
        self.finished = True
        return None

    def update_info(self, text: Any) -> None:
        return None

    def ensure_newline(self) -> None:
        ...

    def set_postfix_str(self, text: str = '', refresh: bool = True) -> None:
        self.extra = text
        return None

    set_postfix = set_postfix_str
    set_extra = set_postfix_str
