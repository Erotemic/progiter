r"""
Progress Manager
----------------

This is watch.utils.manager ported from geowatch.

Example:
    >>> # xdoctest: +REQUIRES(env:DEMO_PROGRESS)
    >>> from progiter.progman import ProgressManager
    >>> import time
    >>> delay = 0.05
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
import os
import weakref

from progiter.progiter import ProgIter


__all__ = ['ProgressManager']

# If truthy disable all threaded rich options
PROGITER_NOTHREAD = os.environ.get('PROGITER_NOTHREAD', 'auto')
if PROGITER_NOTHREAD == 'auto':
    # Use rich outside of slurm
    PROGITER_NOTHREAD = os.environ.get('SLURM_JOBID', '')
else:
    PROGITER_NOTHREAD = bool(PROGITER_NOTHREAD)


LIVE_PROGRESS_MANAGERS = weakref.WeakValueDictionary()


class ManagedProgIter(ProgIter):
    """
    Simple subclass of ProgIter to allowed it to be managed.
    """

    def _set_manager(self, manager):
        self.manager = weakref.proxy(manager)

    def update_info(self, text):
        self.info_text = text
        info_text = getattr(self, 'info_text', None)
        self.ensure_newline()
        if info_text is not None:
            # if self._cursor_at_newline:
            print('+ --- Info --- +')
            print(info_text)
            print('+ ------------ +')
        # self.display_message()

    def update(self, n=1):
        if not self.started:
            self.begin()
        manager = getattr(self, 'manager', None)
        if manager is not None:
            # TODO: vet this, not quite working. The idea is if part of a
            # progress manager and this is not the "tail" progiter (i.e. it
            # isn't the only progiter allowed to be clearing newlines) then we
            # should ensure that the progiter that is allowed to clear the
            # newline has its ensure_newline method called so we can actually
            # write our progress without getting clobbered.
            if len(manager.prog_iters) and manager.prog_iters[-1] is not self:
                manager.prog_iters[-1].ensure_newline()
        super().update(n=n)

    def display_message(self):
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

    """

    def __init__(self, iterable=None, desc=None, total=None, freq=1, initial=0,
                 eta_window=64, clearline=True, adjust=True, time_thresh=2.0,
                 show_times=True, show_wall=False, enabled=True, verbose=None,
                 stream=None, chunksize=None, rel_adjust_limit=4.0,
                 transient=False, manager=None, spinner=False, **kwargs):

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
            self._self_managed = False

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
        addtask_kw = {}
        if desc is not None:
            addtask_kw['description'] = desc
        else:
            addtask_kw['description'] = ''
        addtask_kw['total'] = self.total
        self.task_id = self.manager.rich_progress.add_task(**addtask_kw)
        self.transient = transient
        self.extra = None

    def start(self):
        return self.begin()

    def stop(self):
        return self.end()

    def begin(self):
        if self._self_managed:
            self.manager.start()

    def end(self):
        if self.transient:
            self.remove()
        if self._self_managed:
            self.manager.stop()

    def update(self, n=1):
        self.manager.rich_progress.update(self.task_id, advance=n)

    step = update

    def __iter__(self):
        if not self.enabled:
            yield from self.iterable
        else:
            self.start()
            for item in self.iterable:
                yield item
                self.manager.rich_progress.update(self.task_id, advance=1)
            if self.total is None:
                task = self.manager.rich_progress._tasks[self.task_id]
                self.manager.rich_progress.update(self.task_id, total=task.completed)
            self.stop()

    def remove(self):
        """
        Remove this progress task from its rich manager
        """
        if self.enabled:
            self.manager.rich_progress.remove_task(self.task_id)

    def update_info(self, text):
        if self.enabled:
            # FIXME: remove circular reference
            self.manager.update_info(text)

    def ensure_newline(self):
        ...

    def set_postfix_str(self, text, refresh=True):
        self.extra = text
        parts = [self.desc] if self.desc is not None else []
        if self.extra is not None:
            parts.append(self.extra)
        if self.enabled:
            description = ' '.join(parts)
            self.manager.rich_progress.update(
                self.task_id, description=description, refresh=refresh)

    set_postfix = set_postfix_str
    set_extra = set_postfix_str


class BaseProgIterManager:
    def new(self, *args, **kw):
        return self.progiter(*args, **kw)

    def __call__(self, *args, **kw):
        return self.progiter(*args, **kw)

    def start(self):
        return self

    def begin(self):
        return self.start()

    def stop(self, **kwargs):
        ...

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        self.stop(exc_type=exc_type, exc_val=exc_val, exc_tb=exc_tb)


# Global var
MAIN_RICH_PMAN = None


class _RichProgIterManager(BaseProgIterManager):
    """
    rich specific backend.
    """

    def __init__(self, **kwargs):
        self.prog_iters = []
        self.enabled = kwargs.get('enabled', True)

        self.info_panel = None
        self.rich_progress = None
        self._is_main_manager = None

        self.setup_rich()
        self._active = False

    # Can we make this work?
    # def __del__(self):
    #     if self._active:
    #         self.stop()

    def progiter(self, iterable=None, total=None, desc=None, transient=False, spinner=False, verbose='auto', **kw):
        if not self._active:
            self.start()
        # Fixme remove circular ref
        # self.rich_progress.pman = self
        prog = RichProgIter(
            manager=self, iterable=iterable, total=total, desc=desc,
            transient=transient, spinner=spinner, **kw)
        self.prog_iters.append(prog)
        return prog

    def setup_rich(self):
        global MAIN_RICH_PMAN
        import rich
        import rich.progress
        from rich.console import Group
        from rich.live import Live
        from rich.progress import BarColumn, TextColumn
        from rich.progress import Progress as richProgress
        from rich.progress import SpinnerColumn
        from rich.progress import ProgressColumn, Text
        # from rich.style import Style

        if MAIN_RICH_PMAN is not None:
            self._is_main_manager = False
            self.live_context = None
            self.rich_progress = MAIN_RICH_PMAN.rich_progress
            self.progress_group = MAIN_RICH_PMAN.progress_group
        else:
            self._is_main_manager = True

            class ProgressRateColumn(ProgressColumn):
                """Renders human readable transfer speed."""

                def render(self, task) -> Text:
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
                rich.progress.MofNCompleteColumn(),
                # rich.progress.TransferSpeedColumn(),
                ProgressRateColumn(),
                'eta',
                rich.progress.TimeRemainingColumn(),
                'total',
                rich.progress.TimeElapsedColumn(),
            )
            self.info_panel = None
            self.progress_group = Group(
                # self.info_panel,
                self.rich_progress,
            )
            self.live_context = Live(self.progress_group)
            MAIN_RICH_PMAN = self

    def update_info(self, text):
        from rich.panel import Panel
        if self.info_panel is None:
            self.info_panel = Panel(text)
            self.progress_group.renderables.insert(0, self.info_panel)
        else:
            self.info_panel.renderable = text

    def start(self):
        if self.enabled and not self._active:
            self._active = True
            if self._is_main_manager:
                return self.live_context.__enter__()

    def stop(self, **kw):
        if self.enabled and self._active:
            if not kw:
                kw['exc_type'] = None
                kw['exc_val'] = None
                kw['exc_tb'] = None
            if self._is_main_manager:
                global MAIN_RICH_PMAN
                MAIN_RICH_PMAN = None
                ret = self.live_context.__exit__(**kw)
                self._is_main_manager = False
            else:
                ret = None
            self._active = False
            return ret


class _ProgIterManager(BaseProgIterManager):
    """
    progiter specific backend
    """

    def __init__(self, **kwargs):
        self.enabled = kwargs.get('enabled', True)
        # Default arguments for new progiters
        self.default_progkw = {
            'time_thresh': 2.0,
        }
        self.default_progkw.update(kwargs)
        self.prog_iters = []

    def progiter(self, iterable=None, total=None, desc=None, transient=False, spinner=False, verbose='auto', **kw):
        progkw = self.default_progkw.copy()
        progkw.update(kw)
        progkw['verbose'] = verbose
        if verbose == 'auto':
            progkw['verbose'] = self.default_progkw.get('verbose', 1)
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

    def update_info(self, text):
        if len(self.prog_iters) == 0:
            # if self._cursor_at_newline:
            print('+ --- Info --- +')
            print(text)
            print('+ ------------ +')
        else:
            self.prog_iters[0].update_info(text)


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
    """

    def __init__(self, backend='rich', **kwargs):
        LIVE_PROGRESS_MANAGERS[id(self)] = self

        # TODO: check if we are being tee-d and use progiter instead if we are.

        if PROGITER_NOTHREAD:
            backend = 'progiter'
        if backend == 'rich':
            self.backend = _RichProgIterManager(**kwargs)
        elif backend == 'progiter':
            self.backend = _ProgIterManager(**kwargs)
        else:
            raise KeyError(backend)

    def progiter(self, *args, **kw):
        prog = self.backend.progiter(*args, **kw)
        return prog

    def update_info(self, text):
        self.backend.update_info(text)

    def start(self):
        self.backend.start()

    def stop(self, *args, **kwargs):
        self.backend.stop(*args, **kwargs)

    @property
    def _is_main_manager(self):
        return self.backend._is_main_manager

    @classmethod
    def stopall(self):
        """
        Stop all background progress threads (likely only 1 exists)

        Ignore:
            from progiter import manager
            manager.ProgressManager.stopall()
        """
        for pman in LIVE_PROGRESS_MANAGERS.values():
            pman.stop()
