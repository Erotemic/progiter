from _typeshed import Incomplete
from progiter.progiter import ProgIter

PROGITER_NOTHREAD: Incomplete
LIVE_PROGRESS_MANAGERS: Incomplete


class ManagedProgIter(ProgIter):
    info_text: Incomplete

    def update_info(self, text) -> None:
        ...

    def update(self, n: int = ...) -> None:
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
                 **kwargs) -> None:
        ...

    def start(self):
        ...

    def stop(self):
        ...

    def begin(self) -> None:
        ...

    def end(self) -> None:
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

    def stop(self, **kwargs) -> None:
        ...

    def __enter__(self):
        ...

    def __exit__(self,
                 exc_type: Incomplete | None = ...,
                 exc_val: Incomplete | None = ...,
                 exc_tb: Incomplete | None = ...) -> None:
        ...


MAIN_RICH_PMAN: Incomplete


class _RichProgIterManager(BaseProgIterManager):
    prog_iters: Incomplete
    enabled: Incomplete
    info_panel: Incomplete
    rich_progress: Incomplete
    default_progkw: Incomplete

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

    live_context: Incomplete
    progress_group: Incomplete

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


class ProgressManager(BaseProgIterManager):
    backend: Incomplete

    def __init__(self, backend: str = ..., **kwargs) -> None:
        ...

    def progiter(self, *args, **kw):
        ...

    def update_info(self, text) -> None:
        ...

    def start(self) -> None:
        ...

    def stop(self, *args, **kwargs) -> None:
        ...

    @classmethod
    def stopall(self) -> None:
        ...
