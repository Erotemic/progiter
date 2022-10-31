import utool as ut

from progiter import ProgIter


def time_progiter_overhead():
    # Time the overhead of this function
    import timeit
    import textwrap
    setup = textwrap.dedent(
        '''
        from progiter import ProgIter
        import numpy as np
        import time
        from six.moves import StringIO, range
        # import utool as ut
        N = 500
        file = StringIO()
        rng = np.random.RandomState(42)
        ndims = 2
        vec1 = rng.rand(113, ndims)
        vec2 = rng.rand(71, ndims)

        def minimal_wraper1(sequence):
            for item in sequence:
                yield item

        def minimal_wraper2(sequence):
            for count, item in enumerate(sequence, start=1):
                yield item

        def minimal_wraper3(sequence):
            count = 0
            for item in sequence:
                yield item
                count += 1

        def minwrap4(sequence):
            for count, item in enumerate(sequence, start=1):
                yield item
                if count % 100:
                    pass

        def minwrap5(sequence):
            for count, item in enumerate(sequence, start=1):
                yield item
                if time.time() < 100:
                    pass

        def step_through(prog):
            prog.begin()
            for item in range(prog.total):
                prog.step()
                yield item
            prog.end()
        '''
    )
    statements = {
        'baseline'         : '[{work} for n in range(N)]',
        'creation'         : 'ProgIter(range(N))',
        'minwrap1'         : '[{work} for n in minimal_wraper1(range(N))]',
        'minwrap2'         : '[{work} for n in minimal_wraper2(range(N))]',
        'minwrap3'         : '[{work} for n in minimal_wraper3(range(N))]',
        'minwrap4'         : '[{work} for n in minwrap4(range(N))]',
        'minwrap5'         : '[{work} for n in minwrap5(range(N))]',
        '(sk-disabled)'    : '[{work} for n in ProgIter(range(N), enabled=False, file=file)]',  # NOQA
        '(sk-plain)'       : '[{work} for n in ProgIter(range(N), file=file)]',  # NOQA
        '(sk-freq)'        : '[{work} for n in ProgIter(range(N), file=file, freq=100)]',  # NOQA
        '(sk-no-adjust)'   : '[{work} for n in ProgIter(range(N), file=file, adjust=False, freq=200)]',  # NOQA
        '(sk-high-freq)'   : '[{work} for n in ProgIter(range(N), file=file, adjust=False, freq=200)]',  # NOQA

        # '(ut-disabled)'    : '[{work} for n in ut.ProgIter(range(N), enabled=False, file=file)]',    # NOQA
        # '(ut-plain)'       : '[{work} for n in ut.ProgIter(range(N), file=file)]',  # NOQA
        # '(ut-freq)'        : '[{work} for n in ut.ProgIter(range(N), freq=100, file=file)]',  # NOQA
        # '(ut-no-adjust)'   : '[{work} for n in ut.ProgIter(range(N), freq=200, adjust=False, file=file)]',  # NOQA
        # '(ut-high-freq)'   : '[{work} for n in ut.ProgIter(range(N), file=file, adjust=False, freq=200)]',  # NOQA

        '(step-plain)'      : '[{work} for n in step_through(ProgIter(total=N, file=file))]',  # NOQA
        '(step-freq)'      : '[{work} for n in step_through(ProgIter(total=N, file=file, freq=100))]',  # NOQA
        '(step-no-adjust)' : '[{work} for n in step_through(ProgIter(total=N, file=file, adjust=False, freq=200))]',  # NOQA
    }
    # statements = {
    #     'calc_baseline': '[vec1.dot(vec2.T) for n in range(M)]',  # NOQA
    #     'calc_plain': '[vec1.dot(vec2.T) for n in ProgIter(range(M), file=file)]',  # NOQA
    #     'calc_plain_ut': '[vec1.dot(vec2.T) for n in ut.ProgIter(range(M), file=file)]',  # NOQA
    # }
    timeings = {}

    work_strs = [
        'None',
        'vec1.dot(vec2.T)',
        'n % 10 == 0',
    ]
    work = work_strs[0]
    # work = work_strs[1]

    number = 10000
    prog = ProgIter(desc='timing', adjust=True)
    for key, stmt in prog(statements.items()):
        prog.set_extra(key)
        secs = timeit.timeit(stmt.format(work=work), setup, number=number)
        timeings[key] = secs / number

    print(ut.align(ut.repr4(timeings, precision=8), ':'))


if __name__ == '__main__':
    time_progiter_overhead()
