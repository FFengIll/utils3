import json
import sys
import pickle
from plyvel import DB
from logbook import StreamHandler, Logger
import logging

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
        try:
            self.db = DB(dbpath, create_if_missing=True)
        except Exception as e:
            self.db = None
            raise e
        self.old_key = None
        self.upgrade = False

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
        FIXME: now obey json as much as possible, but we may need pickle
        """
        s = pickle.dumps(data)
        return s

        if isinstance(data, bytes):
            return data
        elif isinstance(data, str):
            return data.encode()
        elif isinstance(data, list) or isinstance(data, dict):
            data = json.dumps(data)
            data = data.encode()
            return data
        elif isinstance(data, tuple):
            data = json.dumps(list(data))
            data = data.encode()
            return data
        elif isinstance(data, int):
            return str(data).encode()
        elif isinstance(data, bool):
            return bytes(data)
        elif data is None:
            # FIXME: how to process `None`
            data = json.dumps([])
            data = data.encode()
            return data

    @staticmethod
    def recover_bytes(data):
        s = data
        return pickle.loads(s)

        data = data.decode()
        try:
            return json.loads(data)
        except:
            return data

    def get(self, k, default=None):
        """
        user shold determine the key exist or not 
        (according to the default)
        """
        logger.debug('key: {}', k, )

        key = self.to_bytes(k)
        res = self.db.get(key, default)

        if res != default:
            res = self.recover_bytes(res)
            logger.debug('get exist: {} -> data(type={}, {})',
                         k, type(res), res if isinstance(res, int) else len(res))

        return res

    def put(self, k, v):
        logger.debug('put: {} -> data(type={}, size={})',
                     k, type(v), v if isinstance(v, int) else len(v))
        key = self.to_bytes(k)
        value = self.to_bytes(v)
        return self.db.put(key, value)

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
                     args, kwargs, positions, keys,)

        key = []
        for p in positions:
            key.append(args[p])
        for k in keys:
            key.append(kwargs[k])
        return key

    def snapshot(self, *_args, ignore=None,  redos=None, **_kwargs):
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

            def inner(*args, **kwargs):
                key = self.get_key(positions, keys, *args, **kwargs)

                if self.upgrade:
                    old_key = self.get_key(
                        self.old_key[0], self.old_key[1], *args, **kwargs)
                    logger.info('will upgrade old_key: {}', old_key)
                    result = self.get(old_key)
                    if result is not None:
                        logger.info('upgrade result: {} -> {} -> {}',
                                    old_key, key, result)
                        self.delete(old_key)
                        self.put(key, result)
                        return result
                else:
                    result = self.get(key)
                    if result is None:
                        pass
                    elif result in _redos:
                        logger.warning('redo result')
                        logging.getLogger().warning('redo result')
                    else:
                        return result

                result = func(*args, **kwargs)

                value = result
                if value != _ignore and value not in _redos:
                    self.put(key, value)
                else:
                    logger.warning('ignore result')


                return result

            return inner

        return do_snapshot


