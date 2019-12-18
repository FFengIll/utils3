import json
import sys
import pickle
from plyvel import DB
from logbook import StreamHandler, Logger
import logging

handler = StreamHandler(sys.stdout, level='WARNING')
handler.push_application()
logger = Logger('data.snapshot')


class Snapshot(object):
    """
    use persistent method (like file, db and so on)
    to store (cache) Output of the Input,
    so we can bypass the known pair to save time/cpu/...
    """

    def __init__(self, dbpath, *args, debug=False, refresh=None, **kwargs):
        """
        :param refresh: ignore data in db and refresh using new value
        """
        super().__init__(*args, **kwargs)
        try:
            self.db = DB(dbpath, create_if_missing=True)
        except Exception as e:
            self.db = None
            raise e
        self.old_key = None
        self.upgrade = False

        if debug:
            handler.level = logging.DEBUG

        if refresh:
            self.refresh = True
        else:
            self.refresh = False

    def __del__(self):
        self.close()

    def __exit__(self):
        self.db.close()

    def __iter__(self):
        for k, v in self.db.iterator():
            yield self.recover_bytes(k), self.recover_bytes(v)

    def __contains__(self, key):
        # raise Exception('we do NOT know which one means EXIST')
        return self.get(key, None) is not None

    def __call__(self, *args, ignore=None, redos=None):
        return self.snapshot(*args, ignore, redos)

    def close(self):
        if self.db:
            self.db.close()
            self.db = None

    @staticmethod
    def to_bytes(data):
        """
        support all basic type.
        but never support recursion data, like List[Dict].
        all data will be translated to bytes if possible.

        use pickle to save bytes so we can store any possible data.
        """
        s = pickle.dumps(data)
        return s

    @staticmethod
    def recover_bytes(data):
        s = data
        return pickle.loads(s)

    def get(self, key, default=None):
        """
        user shold determine the key exist or not
        (according to the default)
        """
        logger.debug('key: {}', key, )

        key = self.to_bytes(key)
        data = self.db.get(key, default)

        if data != default:
            logger.debug('get exist: {} -> data(type={})', key, type(data))

        return data

    def get_result(self, key) -> bytes:
        """
        get the value related to the key,
        return the result by decoding it from bytes
        :param key:
        :return:
        """
        data = self.get(key)
        if data is None:
            return None
        else:
            return self.recover_bytes(data)

    def put(self, k, v):
        logger.debug('put: {} -> data(type={})', k, type(v))
        key = self.to_bytes(k)
        data = self.to_bytes(v)
        return self.db.put(key, data)

    def exist(self, key):
        return key in self

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
                     args, kwargs, positions, keys, )

        key = []
        for p in positions:
            key.append(args[p])
        for k in keys:
            key.append(kwargs[k])
        return key

    def snapshot(self, *_args, ignore=None, redos=None, ignore_callback=None, redo_callback=None):
        """
        the args:
        can be number: the idx/pos of given args
        can be string: the key name in kwargs

        the kwargs:
        some config for snapshot
        """
        logger.debug('choose as key: {}', _args)
        positions, keys = self.get_key_config(*_args)

        # will ignore some return value, aka. no snapshot for it
        _ignore = ignore
        # will redo for some return value, should be a list
        _redos = redos or []

        logger.debug('choose position args: {}', positions)
        logger.debug('choose name kwargs: {}', keys)

        def do_snapshot(func):
            def is_ignore(value):
                if value == _ignore:
                    return True

                if ignore_callback and ignore_callback(value):
                    return True

                return False

            def is_redo(value):
                if value in _redos:
                    return True

                if redo_callback and redo_callback(value):
                    return True

                return False

            def worker(*args, **kwargs):
                key = self.get_key(positions, keys, *args, **kwargs)

                if self.upgrade:
                    old_key = self.get_key(
                        self.old_key[0], self.old_key[1], *args, **kwargs)
                    logger.info('will upgrade old_key: {}', old_key)
                    result = self.get(old_key)
                    if result is not None:
                        result = self.recover_bytes(result)
                        logger.info('upgrade result: {} -> {} -> {}',
                                    old_key, key, result)
                        self.delete(old_key)
                        self.put(key, result)
                        return result
                else:
                    result = self.get(key)
                    if result is None:
                        pass
                    else:
                        result = self.recover_bytes(result)

                        if is_redo(result):
                            logger.warning('redo result: {}', result)
                            logging.getLogger().warning('redo result')
                        elif self.refresh:
                            pass
                        else:
                            return result

                result = func(*args, **kwargs)
                value = result

                if is_ignore(value):
                    logger.warning('ignore result: {}', result)
                elif is_redo(value):
                    logger.warning('redo result: {}', result)
                else:
                    self.put(key, value)

                return result

            return worker

        return do_snapshot
