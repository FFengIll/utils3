"""
基本思路：
支持k,v的dot access。
因为k不能是dot key，e.g. a.b.c，
这样一来就不是很便捷，要想如此这般，就要hook数据。

因此，未匹配时，返回mock object，并关联上下文，以确保可以持续access，
并通过上下文拼接实际的key（with dot），获取对应value。

由于必须要获取到对应的末端数据，即确定的key，value，
所以，不需要支持任何运算，一旦错误使用mock，则报错——用户应当保障使用方式。
"""

from argparse import Namespace
from configparser import SectionProxy


class UnsupportException(Exception):
    pass


class DotMock():
    def __init__(self, key, config):
        self._object = config
        self.key = key

    def __getattr__(self, item):
        dotkey = '{}.{}'.format(self.key, item)
        if dotkey in self._object:
            return self._object[dotkey]
        else:
            return DotMock(dotkey, self._object)


class DotConfig():
    """
    python内置模块，argparse（namespace），configparse（dict） 实际都支持对dot形式的key进行读取（因为是kv，key为str）。
    但在实际使用时，dot key不能作为object进行dot access（如：`key='a.b.c'`，访问为`config.a.b.c`），
    因而进行了wrap，以达到这一个效果。
    """

    def __init__(self, config):
        # only allow some limited type
        if not (isinstance(config, Namespace)
                or isinstance(config, dict)
        ):
            raise UnsupportException

        self._object = config

    def __getattr__(self, item):
        """
        基本属性等同object，未知属性视为配置访问。
        FIXME：存在潜在缺陷，用户给定重名配置；check成本较高，当前由用户保障
        :param item:
        :return:
        """
        if hasattr(self._object, item):
            return getattr(self._object, item)
        else:
            return self[item]

    def __getitem__(self, item):
        if item in self._object:
            return self._object[item]
        else:
            return DotMock(item, self._object)
