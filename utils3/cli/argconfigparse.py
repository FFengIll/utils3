"""
所有参数视为键值对key-value
数据值value有多个来源：
arg.default
arg.userdef
config.value
必须有优先顺序。

优先级：
arg.default < config.value < arg.userdef

即，书写default为默认，从config予以覆盖，再从cli进行覆盖

数据键key有多个来源：
config.key
arg.key

优先级：
arg.key > config.key (待定）

由于arg.dest是确定的，所以，最终的config会全部写入parse的结果中，
所以，key并不会冲突（而是value冲突，以上述优先级定义即可）
"""

from argparse import ArgumentParser, _ArgumentGroup
from configparser import ConfigParser

from io import StringIO
import os

from types import MethodType, FunctionType
from typing import Any

import json


def decorator(func):
    def inner(*args, **kwargs):
        print(args, kwargs)
        res = func(*args, **kwargs)
        return res

    return inner


class ArgConfigSubparser():
    def __init__(self, parent, subparser):
        self._config: ArgConfigParser = parent
        self._object: _ArgumentGroup = subparser

    def __getattr__(self, item):
        return getattr(self._object, item)

    def add_argument(self, *args, **kwargs):
        res = self._object.add_argument(*args, **kwargs)
        return self._config.fix_argument(res)


class ArgConfigGroup():
    def __init__(self, parent, group):
        self._config: ArgConfigParser = parent
        self._object: _ArgumentGroup = group

    def __getattr__(self, item):
        return getattr(self._object, item)

    def add_argument(self, *args, **kwargs):
        res = self._object.add_argument(*args, **kwargs)
        return self._config.fix_argument(res)

    def add_argument_group(self, *args: Any, **kwargs: Any):
        res = self._object.add_argument_group(*args, **kwargs)
        return ArgConfigGroup(self, res)


class ArgConfigParser(ArgumentParser):
    """
    这是一个多继承新式类，同时提供
    `参数解析`，和`配置解析`
    ——使得 默认参数从配置读取，而制定参数可用于覆盖和扩充。

    根据检索，目前argparse和configparser没有函数冲突
    """

    def __init__(self, *args, arg_config=None, **kwargs):
        # must init config first
        config_parser = ConfigParser()
        self.config_parser = config_parser
        if arg_config:
            with StringIO() as fd:
                fd.write('[DEFAULT]\n' + open(arg_config).read())
                fd.seek(0, os.SEEK_SET)
                config_parser.read_file(fd)

        self.config = config_parser[config_parser.default_section]

        self.arg_parser = ArgumentParser(*args, **kwargs)

        super().__init__(*args, **kwargs)

    def __getattribute__(self, name):
        """
        在一定程度上，hook掉argparse中的api
        :param name:
        :return:
        """
        attr = super().__getattribute__(name)

        if isinstance(attr, MethodType) and name == 'add_argument':
            # 当前发现，大量参数添加都会回调到该api，即作为主要hook点

            @decorator
            def inner(*args, **kwargs):
                return attr(*args, **kwargs)

            return inner

        return attr

    def get_config(self, key, ktype=None):
        value = self.config[key]
        if ktype is int:
            return self.config.getint(key)
        elif ktype is float:
            return self.config.getfloat(key)
        elif ktype is bool:
            return self.config.getboolean(key)
        else:
            return value

    def has_config(self, key):
        return key in self.config

    def print_config(self):
        print(self.config)

    def fix_argument(self, res):
        # try to hook and change the default from config
        key = res.dest
        if self.has_config(key):
            res.default = self.get_config(key, res.type) or res.default
        return res

    def add_argument(self, *args, **kwargs):
        res = super().add_argument(*args, **kwargs)

        return self.fix_argument(res)

    def add_argument_group(self, *args: Any, **kwargs: Any):
        res = super().add_argument_group(*args, **kwargs)

        return ArgConfigGroup(self, res)

    def merge(self, args):
        for k, v in self.config.items():
            if not hasattr(args, k):
                setattr(args, k, v)
        return args

    def parse_args(self, *args, **kwargs):
        """
        we call parse, but set default from the config
        :param args:
        :param kwargs:
        :return:
        """

        # FIXME set defaults is work, but the type is undefined
        # must fix the type, so hook is still better
        # self.set_defaults(**dict(self.config))

        origin_args = super().parse_args(*args, **kwargs)

        return self.merge(origin_args)
