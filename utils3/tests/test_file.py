from utils3.file.hash import *

def test_hash_file(tmp_path):
    d = tmp_path / 'testcases'
    d.mkdir()
    filepath = d / 'hashobj'
    filepath.write_text('123')

    res = hash_file('md5', filepath)
    print(res)
    assert res == '202cb962ac59075b964b07152d234b70'
    res = hash_file('sha1', filepath)
    print(res)
    assert res == '40bd001563085fc35165329ea1ff5c5ecbdbbeef'
    res = hash_file('sha256', filepath)
    print(res)
