import ubelt as ub
from progiter import ProgressManager
from concurrent.futures import as_completed


def main():

    pman = ProgressManager(backend='progiter')

    executor = ub.Executor(mode='process', max_workers=4)
    input_rows = [{'x': x, 'name': f'process {x}'} for x in range(100)]
    with pman, executor:

        jobs = []
        for row in pman.progiter(input_rows, desc='submit jobs'):
            job = executor.submit(worker_function, row)
            jobs.append(job)

        _as_completed_iter = as_completed(jobs)
        results = []
        for job in pman.progiter(_as_completed_iter, total=len(jobs), desc='collect jobs', verbose=3):
            result = job.result()
            results.append(result)

    print(f'results = {ub.urepr(results, nl=1)}')


def worker_function(row):
    import time
    y = 0
    name = row['name']
    pman = ProgressManager(backend='progiter')
    with pman:
        for _ in pman.progiter(range(row['x']), desc=f'process {name}', transient=True):
            time.sleep(0.01)
            y += 1

    result = {'y': y}
    return result


if __name__ == '__main__':
    """
    CommandLine:
        python ~/code/progiter/docs/source/manual/examples/threaded_workers.py
    """
    main()
