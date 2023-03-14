import ubelt as ub
import progiter
import timerit


def basic_benchmark():
    """
    Run the simplest benchmark where we iterate over nothing and compare the
    slowdown of using a progress iterator versus doing nothing.
    """
    N = 100_000

    ti = timerit.Timerit(21, bestof=3, verbose=2)
    for timer in ti.reset('baseline'):
        for i in range(N):
            ...

    # for timer in ti.reset('ubelt progiter'):
    #     for i in ub.ProgIter(range(N)):
    #         ...

    for timer in ti.reset('progiter, enabled=False'):
        for i in progiter.ProgIter(range(N), enabled=False):
            ...

    for timer in ti.reset('progiter, homogeneous=True'):
        for i in progiter.ProgIter(range(N), homogeneous=True):
            ...

    for timer in ti.reset('progiter, homogeneous=auto'):
        for i in progiter.ProgIter(range(N), homogeneous='auto'):
            ...

    for timer in ti.reset('progiter, homogeneous=False'):
        for i in progiter.ProgIter(range(N), homogeneous=False):
            ...

    import tqdm
    for timer in ti.reset('tqdm'):
        for i in tqdm.tqdm(range(N)):
            ...

    if 1:
        from rich.live import Live
        from rich.progress import Progress as richProgress
        for timer in ti.reset('rich.progress'):
            prog_manager = richProgress()
            task_id = prog_manager.add_task(description='', total=N)
            live_context = Live(prog_manager)
            with live_context:
                for i in range(N):
                    prog_manager.update(task_id, advance=1)

    import pandas as pd
    df = pd.DataFrame.from_dict(ti.rankings['mean'], orient='index', columns=['mean'])
    df.loc[list(ti.rankings['min'].keys()), 'min'] = list(ti.rankings['min'].values())
    df['mean_rel_overhead'] = df['mean'] / df.loc['baseline', 'mean']
    df['min_rel_overhead']  = df['min'] / df.loc['baseline', 'min']
    print(df.to_string())


def other_tests():
    N = 100
    ###########
    with ub.Timer(label='progiter fixed freq=10'):
        for i in progiter.ProgIter(range(N), freq=10, adjust=False):
            pass

    with ub.Timer(label='ubelt fixed freq=10'):
        for i in ub.ProgIter(range(N), freq=10, adjust=False):
            pass

    with ub.Timer(label='progiter fixed freq=1'):
        for i in progiter.ProgIter(range(N), freq=1, adjust=False):
            pass

    with ub.Timer(label='ubelt fixed freq=1'):
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

if __name__ == '__main__':
    """
    CommandLine:
        python ~/code/progiter/dev/benchmarks/bench_check.py
    """
    basic_benchmark()
