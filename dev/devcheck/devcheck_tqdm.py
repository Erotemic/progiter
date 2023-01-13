import time
import itertools as it  # NOQA


class LongIterable:

    def __init__(self, duration=20):
        self.duration = duration
        n = 1000
        start = time.perf_counter()
        def test_iter():
            for index in range(n):
                yield index
        for _ in test_iter():
            pass
        stop = time.perf_counter()
        stop = time.perf_counter()
        time_per_iter = ((stop - start) / n) * 5  # rough adjustment factor
        num_iters = int((self.duration / time_per_iter))
        self.num_iters = num_iters

    def __len__(self):
        return self.num_iters

    def __iter__(self):
        for index in range(self.num_iters):
            yield index



def check_performance_versus_tqdm():
    import progiter
    import tqdm
    import ubelt as ub

    self = iterable = LongIterable(duration=3)

    progkw = dict(
        leave=True,
        mininterval=2.0,
    )

    with ub.Timer('tqdm') as timer1:
        Progress = tqdm.tqdm
        prog = Progress(iterable, **progkw)
        for idx in prog:
            pass

    with ub.Timer('progiter.progiter') as timer2:
        Progress = progiter.ProgIter
        prog = Progress(iterable, **progkw)
        for idx in prog:
            pass

    with ub.Timer('ub progiter') as timer3:
        Progress = ub.ProgIter
        prog = Progress(iterable, **progkw)
        for idx in prog:
            pass

    print('timer1.elapsed = {!r}'.format(timer1.elapsed))
    print('timer2.elapsed = {!r}'.format(timer2.elapsed))
    print('timer3.elapsed = {!r}'.format(timer3.elapsed))
