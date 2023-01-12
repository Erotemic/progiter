import ubelt as ub
import progiter
import timerit


def basic_test():
    N = 10_000

    ti = timerit.Timerit(10, bestof=3, verbose=2)
    for timer in ti.reset('baseline'):
        for i in range(N):
            ...

    for timer in ti.reset('old progiter'):
        for i in ub.ProgIter(range(N)):
            ...

    for timer in ti.reset('new progiter, enabled=False'):
        for i in progiter.ProgIter(range(N), enabled=False):
            ...

    for timer in ti.reset('new progiter, homogeneous=True'):
        for i in progiter.ProgIter(range(N), homogeneous=True):
            ...

    for timer in ti.reset('new progiter, homogeneous=auto'):
        for i in progiter.ProgIter(range(N), homogeneous='auto'):
            ...

    for timer in ti.reset('new progiter, homogeneous=False'):
        for i in progiter.ProgIter(range(N), homogeneous=False):
            ...

    print(ub.urepr(ti.rankings['mean'], align=':'))





###########
with ub.Timer(label='new fixed freq=10'):
    for i in progiter.ProgIter(range(N), freq=10, adjust=False):
        pass


with ub.Timer(label='old fixed freq=10'):
    for i in ub.ProgIter(range(N), freq=10, adjust=False):
        pass


with ub.Timer(label='new fixed freq=1'):
    for i in progiter.ProgIter(range(N), freq=1, adjust=False):
        pass


with ub.Timer(label='old fixed freq=1'):
    for i in ub.ProgIter(range(N), freq=1, adjust=False):
        pass


import timerit
import time
ti = timerit.Timerit(100000, bestof=10, verbose=2)

for timer in ti.reset('time.process_time()'):
    with timer:
        time.process_time()


for timer in ti.reset('time.process_time_ns()'):
    with timer:
        time.process_time_ns()

for timer in ti.reset('time.time()'):
    with timer:
        time.time()

for timer in ti.reset('time.time_ns()'):
    with timer:
        time.time_ns()

for timer in ti.reset('time.perf_counter()'):
    with timer:
        time.perf_counter()

for timer in ti.reset('time.perf_counter_ns()'):
    with timer:
        time.perf_counter_ns()

for timer in ti.reset('time.thread_time()'):
    with timer:
        time.thread_time()

for timer in ti.reset('time.monotonic()'):
    with timer:
        time.monotonic()

for timer in ti.reset('time.monotonic_ns()'):
    with timer:
        time.monotonic_ns()


print('ti.rankings = {}'.format(ub.repr2(ti.rankings, nl=2, align=':', precision=8)))
