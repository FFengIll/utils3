import json
import sys
from plyvel import DB
from logbook import StreamHandler, Logger

handler = StreamHandler(sys.stdout, level='DEBUG')
handler.push_application()
logger = Logger('data.snapshot')


class Snapshot(object):
    """
    use persistent method (like file, db and so on)
    to store (cache) Output of the Input,
    so we can bypass the known pair to save time/cpu/...
    """
    def __init__(self, dbpath, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = DB(dbpath, create_if_missing=True)
        self.old_key = None
        self.upgrade = False

    def __del__(self):
        self.db.close()
        logger.debug('db closed')

    @staticmethod
    def to_bytes(data):
        if isinstance(data, bytes):
            return data
        elif isinstance(data, str):
            return data.encode()
        elif isinstance(data, list) or isinstance(data, dict):
            data = json.dumps(data)
            data = data.encode()
            return data
        elif isinstance(data, int):
            return str(data).encode()

    @staticmethod
    def recover_bytes(data):
        data = data.decode()
        try:
            return json.loads(data)
        except:
            return data

    def get(self, k):
        logger.debug('key: {}', k, )

        key = self.to_bytes(k)
        res = self.db.get(key, None)

        if res is not None:
            res = self.recover_bytes(res)

        logger.debug('get: {} -> {}', k, res)

        return res

    def put(self, k, v):
        logger.debug('put: {} -> {}', k, v)
        key = self.to_bytes(k)
        value = self.to_bytes(v)
        return self.db.put(key, value)

    def delete(self, k):
        key = self.to_bytes(k)
        return self.db.delete(key)

    def set_upgrade(self, *old_args):
        positions, keys = self.get_key_config(*old_args)
        self.upgrade = True
        self.old_key = positions, keys

    @staticmethod
    def get_key_config(*args):
        positions, keys = [], []
        for item in args:
            if isinstance(item, int):
                positions.append(item)
            elif isinstance(item, str):
                keys.append(item)
        return positions, keys

    def get_key(self, positions, keys, *args, **kwargs):
        logger.debug('get key from {} {} (positions:{} keys:{})',
                     args, kwargs, positions, keys,)

        key = []
        for p in positions:
            key.append(args[p])
        for k in keys:
            key.append(kwargs[k])
        return key

    def snapshot(self, *_args, **_kwargs):
        logger.debug('choose as key: {}', _args)
        positions, keys = self.get_key_config(*_args)

        logger.debug('choose position args: {}', positions)
        logger.debug('choose name kwargs: {}', keys)

        def do_snapshot(func):

            def inner(*args, **kwargs):
                key = self.get_key(positions, keys, *args, **kwargs)

                if self.upgrade:
                    old_key = self.get_key(
                        self.old_key[0], self.old_key[1], *args, **kwargs)
                    logger.info('will upgrade old_key: {}', old_key)
                    result = self.get(old_key)
                    if result is not None:
                        logger.info('exist old result: {} -> {}',
                                    old_key, result)
                        logger.info('upgrade result: {} -> {}', key, result)
                        self.delete(old_key)
                        self.put(key, result)
                        return result
                else:
                    result = self.get(key)
                    if result is not None:
                        logger.info('exist result: {} -> {}', key, result)
                        return result

                result = func(*args, **kwargs)
                logger.info('new result : {} -> {}', key, result)

                value = result
                self.put(key, value)

                return result

            return inner

        return do_snapshot


def test_kv():
    app = Snapshot('./db')

    @app.snapshot(1, 2, 'info', 'extra')
    def inner(a, b, c, **kwargs):
        print(kwargs)
        return a+b+c

    res = inner(5, 6, 1, info='test', extra=None)

    assert res == app.get([6, 1, 'test', None])


def test_upgrade():
    app = Snapshot('./db')

    # old
    @app.snapshot(1, 2, 'info')
    def inner(a, b, c, **kwargs):
        print(kwargs)
        return a+b+c
    res = inner(5, 6, 1, info='test', extra=None)

    # new
    app.set_upgrade(1, 2, 'info')

    @app.snapshot(1, 2, 'info', 'extra')
    def inner(a, b, c, **kwargs):
        print(kwargs)
        return a+b+c
    res = inner(5, 6, 1, info='test', extra=None)

    assert res == app.get([6, 1, 'test', None])


if __name__ == "__main__":
    test()
