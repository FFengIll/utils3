"""
a set of simple logic to determine the data code mode (encode/decode mode), e.g. base64, gzip and so on
"""

from typing import ClassVar
from inspect import isfunction
import traceback
import types

from utils3.cli.logger import get_logger

log = get_logger('{}.{}'.format(__package__, __file__), 'DEBUG')


class Detector():
    def __init__(self):
        self.detectors = set()

    def check(self, data: bytes):
        count = 0
        for func in self.detectors:
            try:
                res = func(data)
                if res:
                    count += 1
            except:
                traceback.print_exc()
        if count <= 0:
            log.warning('found nothing we know')
        return count

    def register_function(self, func):
        """Register a function as a plug-in"""
        self.detectors.add(func)
        return func

    def register_class(self, cls: object):

        for k, v in cls.__dict__.items():
            if isinstance(v, types.FunctionType):
                self.register_function(v)

        return cls


detector = Detector()


class Mode:
    pass


@detector.register_class
class ZipMode(Mode):
    """
    - 0x1F 0x8B 为 deflate，且为 gzip 封装
    - zip 0x1F 0x8B 开头（deflate）
      - 0x78 0x9c 开头(标准压缩)
      - 0x78 0xda 开头（最高压缩）
    - gzip 是一种数据格式，是对 deflate 的封装
    """

    def zip_(data: bytes):
        head = [0x78, 0x9c]
        tmp = list(data)
        if tmp[:2] == head:
            log.info('zip head: standard')
            return True

    def zip_high(data: bytes):
        head = [0x78, 0xda]
        tmp = list(data)
        if tmp[:2] == head:
            log.info('zip head: high level')
            return True

    def gzip(data: bytes):
        head = [0x1f, 0x8b]
        tmp = list(data)
        if tmp[:2] == head:
            log.info('zip head: deflate (algorithm) and gzip (struct)')
            return True


@detector.register_class
class Base64Mode(Mode):
    def b64(self):
        pass


def test_zip():
    import array
    data = [0x78, 0x9c]
    data = array.array('B', data).tobytes()
    assert ZipMode.zip_(data)

    data = [0x78, 0xda]
    data = array.array('B', data).tobytes()
    assert ZipMode.zip_high(data)

    data = [0x1f, 0x8b]
    data = array.array('B', data).tobytes()
    assert ZipMode.gzip(data)


def test_decorator():
    print(detector.detectors)

    assert len(detector.detectors) > 0


def test_detector():
    import array
    data = [0x1f, 0x8b]
    data = array.array('B', data).tobytes()
    assert detector.check(data) > 0
