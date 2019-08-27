from utils3.data.snapshot import *

import pytest
import logging


def test_kv(tmpdir):
    path = tmpdir.mkdir('kv')
    app = Snapshot(str(path))

    # old
    @app.snapshot(1, 2, 'info')
    def inner(a, b, c, **kwargs):
        print(kwargs)
        return a + b + c

    res = inner(5, 6, 1, info='test', extra=None)

    assert res == app.get_result([6, 1, 'test'])

    # new
    app.set_upgrade(1, 2, 'info')

    @app.snapshot(1, 2, 'info', 'extra')
    def inner(a, b, c, **kwargs):
        print(kwargs)
        return a + b + c

    res = inner(5, 6, 1, info='test', extra=None)

    assert res == app.get_result([6, 1, 'test', None])


def test_null(tmpdir):
    path = tmpdir.mkdir('null')
    app = Snapshot(str(path))

    @app.snapshot(1, 2, 'info')
    def inner(a, b, c, **kwargs):
        print(kwargs)
        return []

    res = inner(5, 6, 1, info='test', extra=None)
    db_value = app.get_result([6, 1, 'test'])
    print(res)
    print(db_value)
    assert res == db_value


def test_invalid(tmpdir):
    path = tmpdir.mkdir('invalid')
    app = Snapshot(str(path))

    @app.snapshot(1, 2, 'info', ignore=[])
    def inner(a, b, c, **kwargs):
        print(kwargs)
        return []

    res = inner(5, 6, 1, info='test', extra=None)
    db_value = app.get_result([6, 1, 'test'])
    assert db_value is None


def test_redo(tmpdir, caplog):
    # with caplog.at_level(logging.WARNING, logger="data.snapshot"):

    path = tmpdir.mkdir('redo')
    app = Snapshot(str(path))

    @app.snapshot(1, 2, 'info', redos=[[]])
    def inner(a, b, c, **kwargs):
        print(kwargs)
        return []

    db_value = app.put([6, 1, 'test'], [])
    db_value = app.get_result([6, 1, 'test'])
    assert db_value == []

    res = inner(5, 6, 1, info='test', extra=None)

    redo = False
    for record in caplog.records:
        if record.message == 'redo result':
            redo = True
    assert redo == True


def test_iter(tmpdir):
    path = tmpdir.mkdir('iter')
    app = Snapshot(str(path))

    for k, v in app:
        print(k, v)


def test_op(tmpdir):
    path = tmpdir.mkdir('op')
    app = Snapshot(str(path))

    key = ['test_put']

    app.get_result(key)

    right = ['test_put']
    app.put(key, right)
    left = app.get_result(key)
    assert left == right

    right = 'test_put'
    app.put(key, 'test_put')
    left = app.get_result(key)
    assert left == right

    print(app.exist(key))


if __name__ == "__main__":
    test()
