from utils3.data.snapshot import *

import pytest
import logging


def test_kv():
    app = Snapshot('./db/kv')

    # old
    @app.snapshot(1, 2, 'info')
    def inner(a, b, c, **kwargs):
        print(kwargs)
        return a+b+c

    res = inner(5, 6, 1, info='test', extra=None)

    assert res == app.get([6, 1, 'test'])

    # new
    app.set_upgrade(1, 2, 'info')

    @app.snapshot(1, 2, 'info', 'extra')
    def inner(a, b, c, **kwargs):
        print(kwargs)
        return a+b+c
    res = inner(5, 6, 1, info='test', extra=None)

    assert res == app.get([6, 1, 'test', None])


def test_null():
    app = Snapshot('./db/null')

    @app.snapshot(1, 2, 'info')
    def inner(a, b, c, **kwargs):
        print(kwargs)
        return []
    res = inner(5, 6, 1, info='test', extra=None)
    db_value = app.get([6, 1, 'test'])
    print(res)
    print(db_value)
    assert res == db_value


def test_invalid():
    app = Snapshot('./db/invalid')

    @app.snapshot(1, 2, 'info', invalid=[])
    def inner(a, b, c, **kwargs):
        print(kwargs)
        return []
    res = inner(5, 6, 1, info='test', extra=None)
    db_value = app.get([6, 1, 'test'], default=Exception)
    assert db_value == Exception


def test_redo(caplog):
    # with caplog.at_level(logging.WARNING, logger="data.snapshot"):

    app = Snapshot('./db/redo')

    @app.snapshot(1, 2, 'info', redos=[[]])
    def inner(a, b, c, **kwargs):
        print(kwargs)
        return []

    res = inner(5, 6, 1, info='test', extra=None)
    db_value = app.get([6, 1, 'test'], default=Exception)
    res = inner(5, 6, 1, info='test', extra=None)

    redo = False
    for record in caplog.records:
        if record.message == 'redo result':
            redo = True
    assert redo == True


def test_iter():
    app = Snapshot('./db/iter')

    for k, v in app:
        print(k, v)


def test_op():
    app = Snapshot('./db/op')

    key = ['test_put']

    app.get(key)

    right = ['test_put']
    app.put(key, right)
    left = app.get(key)
    assert left == right

    right = 'test_put'
    app.put(key, 'test_put')
    left = app.get(key)
    assert left == right

    print(app.exist(key))


if __name__ == "__main__":
    test()
