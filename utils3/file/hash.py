"""
open-box api: hash file.
"""
from hashlib import md5, sha1
import hashlib


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


def test():
    filepath = 'testcases/hashobj'
    res = hash_file('md5', filepath)
    print(res)
    assert res == '202cb962ac59075b964b07152d234b70'
    res = hash_file('sha1', filepath)
    print(res)
    assert res == '40bd001563085fc35165329ea1ff5c5ecbdbbeef'
    res = hash_file('sha256', filepath)
    print(res)
