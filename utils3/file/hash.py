"""
open-box api: hash file.
"""
from hashlib import md5, sha1
import hashlib
from io import StringIO, BytesIO


def hash_file(method, filepath):
    hash_method = getattr(hashlib, method, None)
    if hash_method is None:
        raise Exception('not support hash: {}'.format(method))

    with open(filepath, 'rb') as fd:
        hasher = hash_method()
        while 1:
            d = fd.read(8096)
            if not d:
                break
            hasher.update(d)
        hash_code = hasher.hexdigest()
        res = str(hash_code).lower()

    return res


def _md5(io):
    md5_obj = hashlib.md5()
    while 1:
        d = io.read(8096)
        if not d:
            break
        md5_obj.update(d)
    hash_code = md5_obj.hexdigest()
    res = str(hash_code).lower()
    return res


def md5_bytes(data):
    io = BytesIO(data)
    return _md5(io)


def md5_file(filepath):
    # may cause some error!
    with open(filepath, 'rb') as fd:
        md5_obj = hashlib.md5()
        while 1:
            d = fd.read(8096)
            if not d:
                break
            md5_obj.update(d)
        hash_code = md5_obj.hexdigest()
        res = str(hash_code).lower()

    return res
