"""
a set of simple logic to determine the obj code mode (encode/decode mode), e.g. base64, gzip and so on
"""

from typing import ClassVar
from inspect import isfunction
import traceback
import types
from inspect import isfunction

from utils3.cli.logger import get_logger

log = get_logger('{}.{}'.format(__package__, __file__), 'DEBUG')


class Detector():
    def __init__(self):
        self.detectors = set()

    def check(self, obj):
        count = 0
        for func in self.detectors:
            try:
                res = func(obj)
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
class SomeMode(Mode):
    """
    - 0x1F 0x8B 为 deflate，且为 gzip 封装
    - zip 0x1F 0x8B 开头（deflate）
      - 0x78 0x9c 开头(标准压缩)
      - 0x78 0xda 开头（最高压缩）
    - gzip 是一种数据格式，是对 deflate 的封装
    """

    def is_function(obj):
        """
        the function is only a pure function
        :return:
        """
        if isinstance(obj, types.FunctionType):
            log.info('method')
            return True

    def is_method(obj):
        """
        of cource a method from a class
        :return:
        """
        if isinstance(obj, types.MethodType):
            log.info('method')
            return True

    def is_call(obj):
        if hasattr(obj, '__call__'):
            log.info('__call__')
            return True


def test_decorator():
    print(detector.detectors)

    assert len(detector.detectors) > 0


def test_detector():
    assert detector.check(SomeMode.is_function) > 0
