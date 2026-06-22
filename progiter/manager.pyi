from _typeshed import Incomplete
from progiter.progiter import ProgIter

PROGITER_NOTHREAD: Incomplete
LIVE_PROGRESS_MANAGERS: Incomplete


def _coerce_envflag(value) -> bool:
    ...

def _coerce_choice(value, choices, name):
    ...

def _rich_is_available() -> bool:
    ...

def _detect_notebook() -> bool:
    ...

def _stream_is_tty(stream=...) -> bool:
    ...

def _get_current_rich_manager():
    ...

def _normalize_progkw(default_progkw, verbose, kw):
    ...

def _choose_auto_backend(auto_policy: str = ..., stream=..., enabled: bool = ...) -> str:
    ...


class ManagedProgIter(ProgIter):
    info_text: Incomplete

    def update_info(self, text) -> None:
        ...

    def update(self, n: int = ...) -> None:
        ...

    def end(self):
        ...

    def display_message(self) -> None:
        ...


class RichProgIter:
    manager: Incomplete
    iterable: Incomplete
    enabled: Incomplete
    spinner: Incomplete
    total: Incomplete
    desc: Incomplete
    task_id: Incomplete
    transient: Incomplete
    extra: Incomplete
    initial: int
    started: bool
    finished: bool
    freq: int
    time_thresh: Incomplete
    unknown_total_policy: str
    refresh_policy: str

    def __init__(self,
                 iterable: Incomplete | None = ...,
                 desc: Incomplete | None = ...,
                 total: Incomplete | None = ...,
                 freq: int = ...,
                 initial: int = ...,
                 eta_window: int = ...,
                 clearline: bool = ...,
                 adjust: bool = ...,
                 time_thresh: float = ...,
                 show_times: bool = ...,
                 show_wall: bool = ...,
                 enabled: bool = ...,
                 verbose: Incomplete | None = ...,
                 stream: Incomplete | None = ...,
                 chunksize: Incomplete | None = ...,
                 rel_adjust_limit: float = ...,
                 transient: bool = ...,
                 manager: Incomplete | None = ...,
                 spinner: bool = ...,
                 unknown_total_policy: str = ...,
                 refresh_policy: str = ...,
                 _self_managed: bool = ...,
                 **kwargs) -> None:
        ...

    def start(self):
        ...

    def stop(self):
        ...

    def begin(self):
        ...

    def end(self):
        ...

    def update(self, n: int = ...) -> None:
        ...

    step = update

    def __iter__(self):
        ...

    def remove(self) -> None:
        ...

    def update_info(self, text) -> None:
        ...

    def ensure_newline(self) -> None:
        ...

    def set_postfix_str(self, text, refresh: bool = ...) -> None:
        ...

    set_postfix = set_postfix_str
    set_extra = set_postfix_str


class BaseProgIterManager:

    def new(self, *args, **kw):
        ...

    def __call__(self, *args, **kw):
        ...

    def start(self):
        ...

    def begin(self):
        ...

    def stop(self, **kwargs):
        ...

    def __enter__(self):
        ...

    def __exit__(self,
                 exc_type: Incomplete | None = ...,
                 exc_val: Incomplete | None = ...,
                 exc_tb: Incomplete | None = ...):
        ...


class _RichProgIterManager(BaseProgIterManager):
    prog_iters: Incomplete
    enabled: Incomplete
    info_panel: Incomplete
    rich_progress: Incomplete
    default_progkw: Incomplete
    live_context: Incomplete
    progress_group: Incomplete
    _is_main_manager: bool

    def __init__(self, **kwargs) -> None:
        ...

    def _deregister_progiter(self, prog) -> None:
        ...

    def _ensure_attached(self):
        ...

    def progiter(self,
                 iterable: Incomplete | None = ...,
                 total: Incomplete | None = ...,
                 desc: Incomplete | None = ...,
                 transient: bool = ...,
                 spinner: bool = ...,
                 verbose: str = ...,
                 **kw):
        ...

    def setup_rich(self):
        ...

    def update_info(self, text) -> None:
        ...

    def start(self):
        ...

    def stop(self, **kw):
        ...


class _ProgIterManager(BaseProgIterManager):
    enabled: Incomplete
    default_progkw: Incomplete
    prog_iters: Incomplete
    _is_main_manager: bool

    def __init__(self, **kwargs) -> None:
        ...

    def _deregister_progiter(self, prog) -> None:
        ...

    def progiter(self,
                 iterable: Incomplete | None = ...,
                 total: Incomplete | None = ...,
                 desc: Incomplete | None = ...,
                 transient: bool = ...,
                 spinner: bool = ...,
                 verbose: str = ...,
                 **kw):
        ...

    def update_info(self, text) -> None:
        ...


class ProgressManager(BaseProgIterManager):
    backend: Incomplete
    backend_key: str
    requested_backend: str
    auto_policy: str

    def __init__(self, backend: str = ..., **kwargs) -> None:
        ...

    def progiter(self, *args, **kw):
        ...

    def update_info(self, text) -> None:
        ...

    def start(self):
        ...

    def stop(self, *args, **kwargs):
        ...

    @property
    def _is_main_manager(self) -> bool:
        ...

    @classmethod
    def stopall(cls, backend: str | None = ..., raise_errors: bool = ...) -> list[Exception]:
        ...


class _NullProgIterManager(BaseProgIterManager):
    enabled: bool
    default_progkw: Incomplete
    prog_iters: Incomplete
    _is_main_manager: bool

    def __init__(self, **kwargs) -> None:
        ...

    def progiter(self,
                 iterable: Incomplete | None = ...,
                 total: Incomplete | None = ...,
                 desc: Incomplete | None = ...,
                 transient: bool = ...,
                 spinner: bool = ...,
                 verbose: str = ...,
                 **kw):
        ...

    def update_info(self, text) -> None:
        ...

    def _deregister_progiter(self, prog) -> None:
        ...


class _NullProgIter:
    iterable: Incomplete
    desc: Incomplete
    total: Incomplete
    initial: Incomplete
    transient: Incomplete
    manager: Incomplete
    spinner: Incomplete
    enabled: bool
    started: bool
    finished: bool
    extra: Incomplete

    def __init__(self,
                 iterable: Incomplete | None = ...,
                 desc: Incomplete | None = ...,
                 total: Incomplete | None = ...,
                 initial: int = ...,
                 transient: bool = ...,
                 manager: Incomplete | None = ...,
                 spinner: bool = ...,
                 **kwargs) -> None:
        ...

    def __iter__(self):
        ...

    def begin(self):
        ...

    start = begin

    def end(self):
        ...

    stop = end

    def update(self, n: int = ...) -> None:
        ...

    step = update

    def remove(self) -> None:
        ...

    def update_info(self, text) -> None:
        ...

    def ensure_newline(self) -> None:
        ...

    def set_postfix_str(self, text: str = ..., refresh: bool = ...) -> None:
        ...

    set_postfix = set_postfix_str
    set_extra = set_postfix_str
