
def test_multiple_managers():
    """
    Note:
        We want the user to be able let the user create multiple
        ProgressManagers, but we are only allowed one live display, therefore
        the first ProgressManager needs to becomes the "main" manager and all
        others will be secondary. Getting this exactly right may require a
        refactor and locks, but this tests that our simple implementation works
        well enough.
    """
    from progiter import manager
    import time
    try:
        from rich import print
    except ImportError:
        import pytest
        pytest.skip('no rich')

    pman1 = manager.ProgressManager()

    with pman1:
        print(f'pman1._is_main_manager={pman1._is_main_manager}')
        print('Print before loop 1')

        for i in pman1.progiter(range(100), desc='PMAN(1) Iter(1)'):
            time.sleep(0.01)

        print('Print after loop 1 #1')
        print('Print after loop 1 #2')
        print('Print after loop 1 #3')

        print('Print before loop 2')

        for i in pman1.progiter(range(100), desc='PMAN(1) Iter(2)'):
            time.sleep(0.009)

        print('Print after loop 2 #1')
        print('Print after loop 2 #2')
        print('Print after loop 2 #3')

        pman2 = manager.ProgressManager()
        print(f'pman2._is_main_manager={pman2._is_main_manager}')

        for idx in range(2):
            for i in pman2.progiter(range(100), desc=f'PMAN(2) Iter({idx})'):
                time.sleep(0.008)

        print(f'pman2._is_main_manager={pman2._is_main_manager}')
        print(f'pman1._is_main_manager={pman1._is_main_manager}')

    print(f'pman1._is_main_manager={pman1._is_main_manager}')

    pman3 = manager.ProgressManager()
    print(f'pman3._is_main_manager={pman3._is_main_manager}')
    with pman3:
        print(f'pman3._is_main_manager={pman3._is_main_manager}')
        for idx in range(3):
            for i in pman2.progiter(range(100), desc=f'PMAN(3) Iter({idx})'):
                time.sleep(0.005)
        print(f'pman3._is_main_manager={pman3._is_main_manager}')

    print(f'pman1._is_main_manager={pman1._is_main_manager}')


def test_multiple_managers_tree():
    """
    """
    try:
        import rich  # NOQA
    except ImportError:
        import pytest
        pytest.skip('no rich')
    import time
    from progiter import manager

    sleep_time = 0.001

    def _nested_loop(max_depth=0):

        pman = manager.ProgressManager()
        with pman:
            prog1 = pman.progiter(range(100), desc=f'P1: max_depth={max_depth}')
            for i in zip(prog1, range(50)):
                time.sleep(sleep_time)
                yield None

            if max_depth > 0:
                yield from _nested_loop(max_depth=max_depth - 1)

            for i in zip(prog1, range(50)):
                time.sleep(sleep_time)
                yield None

            if max_depth > 0:
                yield from _nested_loop(max_depth=max_depth - 1)

            prog2 = pman.progiter(range(91), desc=f'P2: max_depth={max_depth}')
            for i in prog2:
                time.sleep(sleep_time)
                yield None

    list(_nested_loop(max_depth=3))
