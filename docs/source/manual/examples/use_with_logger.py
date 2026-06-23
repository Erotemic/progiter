import progiter
import logging

logger = logging.getLogger(__name__)


class LoggerStreamWrapper:
    def __init__(self, logger):
        self.logger = logger

    def flush(self):
        ...

    def write(self, msg):
        self.logger.info(msg.rstrip())


def main():
    logging.basicConfig()
    logger.setLevel(logging.INFO)

    logger.info('Hi, this is an info message')

    wrapper = LoggerStreamWrapper(logger)
    iterable = list(range(100))

    kwargs = dict(
        time_thresh=0,
        # adjust=0,
        # freq=1,
        # verbose=3,
        show_wall=True
    )

    prog = progiter.ProgIter(iterable, stream=wrapper, **kwargs)
    for idx in prog:
        ...

    # prog = progiter.ProgIter(iterable, **kwargs)
    # for idx in prog:
    #     ...


if __name__ == '__main__':
    """
    CommandLine:
        python use_with_logger.py
    """
    main()
