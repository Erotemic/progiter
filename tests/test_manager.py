
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


def test_backend_auto_and_noop_modes():
    from progiter import manager

    pman = manager.ProgressManager(backend='auto', auto_policy='progiter')
    assert pman.backend_key == 'progiter'

    pman = manager.ProgressManager(backend='auto', enabled=False)
    assert pman.backend_key == 'none'
    assert list(pman.progiter(range(3))) == [0, 1, 2]
    assert pman.update_info('silent') is None


def test_context_manager_returns_public_manager():
    from progiter import manager

    pman = manager.ProgressManager(backend='progiter', enabled=False)
    with pman as active:
        assert active is pman


def test_explicit_rich_does_not_fallback(monkeypatch):
    from progiter import manager
    import builtins
    import pytest

    real_import = builtins.__import__

    def blocked_import(name, *args, **kwargs):
        if name == 'rich' or name.startswith('rich.'):
            raise ImportError('blocked rich import')
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, '__import__', blocked_import)
    with pytest.raises(ImportError):
        manager.ProgressManager(backend='rich')


def test_auto_rich_fallback_when_unavailable(monkeypatch):
    from progiter import manager

    monkeypatch.setattr(manager, '_rich_is_available', lambda: False)
    pman = manager.ProgressManager(backend='auto', auto_policy='rich')
    assert pman.backend_key == 'progiter'


def test_stopall_is_exception_safe(monkeypatch):
    from progiter import manager

    class Broken:
        backend_key = 'broken'

        def stop(self):
            raise RuntimeError('expected cleanup failure')

    broken = Broken()
    manager.LIVE_PROGRESS_MANAGERS[id(broken)] = broken
    errors = manager.ProgressManager.stopall(backend='broken')
    assert len(errors) == 1
    assert isinstance(errors[0], RuntimeError)


def test_rich_self_managed_loop_stops():
    try:
        import rich  # NOQA
    except ImportError:
        import pytest
        pytest.skip('no rich')
    from progiter import manager

    pman = manager.ProgressManager(backend='rich')
    assert pman.backend._active is False
    assert list(pman.progiter(range(3), freq=100, time_thresh=999)) == [0, 1, 2]
    assert pman.backend._active is False


def test_rich_unknown_total_policy_and_throttling(monkeypatch):
    try:
        import rich  # NOQA
    except ImportError:
        import pytest
        pytest.skip('no rich')
    from progiter import manager

    pman = manager.ProgressManager(backend='rich')
    calls = []
    original_update = pman.backend.rich_progress.update

    def counting_update(*args, **kwargs):
        calls.append((args, kwargs))
        return original_update(*args, **kwargs)

    monkeypatch.setattr(pman.backend.rich_progress, 'update', counting_update)
    prog = pman.progiter(
        iter(range(5)), total=None, freq=100, time_thresh=999,
        unknown_total_policy='complete')
    assert list(prog) == [0, 1, 2, 3, 4]
    assert prog._completed == 5
    assert prog.finished is True
    # We should not update rich once per item when throttling is active.
    assert len(calls) < 5
