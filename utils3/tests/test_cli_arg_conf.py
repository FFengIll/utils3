from utils3.cli.argconfigparse import *
import pytest


def test_decorator():
    parser = ArgConfigParser()
    parser.add_argument('-a', action='store')
    parser.add_argument('-b', action='store')


def test_change_default():
    parse = ArgConfigParser()
    res = parse.add_argument('-a', default='000', action='store')
    args = parse.parse_args([])
    print(args)
    assert args.a == '000'

    res.default = '123'
    args = parse.parse_args([])
    print(args)
    assert args.a == '123'


@pytest.fixture()
def config_file(tmp_path):
    file = tmp_path / 'default.config'
    file.write_text((
        'a=1\n'
        'a.b.c=1\n'
        'a_b_c=1\n'
    ))
    return file


def test_config_default(config_file):
    parser = ArgConfigParser(arg_config=config_file)
    parser.add_argument('-a', action='store')
    args = parser.parse_args([])
    parser.print_config()
    assert args.a == '1'

    parser = ArgConfigParser(arg_config=config_file)
    parser.add_argument('-a', action='store', type=int)
    parser.add_argument('-dotabc', dest='a.b.c', action='store', type=int)
    parser.add_argument('-lineabc', dest='a_b_c', action='store', type=int)
    args = parser.parse_args([])
    parser.print_config()
    assert args.a == 1
    assert args.a_b_c == 1
    assert getattr(args, 'a.b.c') == 1


def test_group(config_file):
    parser = ArgConfigParser(arg_config= config_file)
    group = parser.add_argument_group('test')
    group.add_argument('-a', action='store', type=int)
    args = parser.parse_args([])
    parser.print_config()
    assert args.a is 1


def test_copy_construct():
    class A:
        def __init__(self):
            self.a=1
    class B(A):
        def __init__(self,parent):
            self.b=2
            super().__init__()
            self= parent

    a=A()
    a.a=10
    b=B(a)
    print(a.a,b.a,b.b)