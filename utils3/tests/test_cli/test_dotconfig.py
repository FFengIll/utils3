from utils3.cli.dotconfig import *
from utils3.tests.test_cli.fixtures import config_file,section_config_file

import configparser
import argparse

import pytest


def test_dot(section_config_file):
    config = configparser.ConfigParser()
    config.read(section_config_file)
    print(list(config.defaults().items()))
    return config.defaults()


def test_dot_conf(section_config_file):
    config = configparser.ConfigParser()
    config.read(section_config_file)
    print(list(config.defaults().items()))
    config = config.defaults()

    obj = DotConfig(config)
    print(obj.dot.a.b.c)

def test_init(section_config_file):
    config = configparser.ConfigParser()
    config.read(section_config_file)
    print(list(config.defaults().items()))
    config = config.defaults()
    obj = DotConfig(config)


    parser = argparse.ArgumentParser()
    parser.add_argument('test')
    args = parser.parse_args()
    obj = DotConfig(args)

    # with pytest.raises(UnsupportException):
    obj = DotConfig({})

    with pytest.raises(UnsupportException):
        obj = DotConfig([])


