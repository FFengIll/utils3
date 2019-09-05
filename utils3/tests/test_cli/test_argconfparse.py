import pytest

from utils3.cli.argconfigparse import *
from utils3.tests.test_cli.fixtures import config_file, section_config_file


def test_argconfparse(tmpdir):
    file = tmpdir.join('default.conf')
    file.write(
        '''
        uri = 127.0.0.1
        username = neo4j
        password = neo4j
        workers = 4
        '''
    )

    parser = ArgConfigParser()
    parser.add_argument('--uri', action='store')
    parser.add_argument('-u', '--user', action='store')
    parser.add_argument('-p', '--password', action='store')
    parser.add_argument('-w', dest='workers', type=int)

    parser.parse_config_file(file)
    args = parser.parse_args('-p not_neo4j'.split())

    assert args.uri == '127.0.0.1'
    assert args.workers == 4
    assert args.password == 'not_neo4j'


def test_decorator():
    parser = ArgConfigParser()
    parser.add_argument('-a', action='store')
    parser.add_argument('-b', action='store')


def test_change_default_config():
    parse = ArgConfigParser()
    res = parse.add_argument('-a', default='000', action='store')
    args = parse.parse_args([])
    print(args)
    assert args.a == '000'

    res.default = '123'
    args = parse.parse_args([])
    print(args)
    assert args.a == '123'


def test_default_config(config_file):
    parser = ArgConfigParser(arg_config=config_file)
    parser.add_argument('-a', action='store')
    args = parser.parse_args([])
    parser.pp()
    assert args.a == '1'

    parser = ArgConfigParser(arg_config=config_file)
    parser.add_argument('-a', action='store', type=int)
    parser.add_argument('-dotabc', dest='a.b.c', action='store', type=int)
    parser.add_argument('-lineabc', dest='a_b_c', action='store', type=int)
    args = parser.parse_args([])
    parser.pp()
    assert args.a == 1
    assert args.a_b_c == 1
    assert getattr(args, 'a.b.c') == 1


def test_group(config_file):
    parser = ArgConfigParser(arg_config=config_file)
    group = parser.add_argument_group('test')
    group.add_argument('-a', action='store', type=int)
    args = parser.parse_args([])
    parser.pp()
    assert args.a is 1


def test_argument_type(config_file):
    parser = ArgConfigParser(arg_config=config_file)
    parser.add_argument('-int', action='store', type=int)
    parser.add_argument('-str', action='store', type=str)
    # parser.add_argument('-list', action='store', type=list)
    # parser.add_argument('-dict', action='store', type=dict)
    args = parser.parse_args([])
    parser.pp()
    assert args.int == 1
    assert args.str == "1"
    # assert args.list == [1]
    # assert args.dict == {'1': 1}


def test_merge_args(config_file):
    parser = ArgConfigParser(arg_config=config_file)
    parser.add_argument('-int', action='store', type=int)

    args = parser.parse_args([])
    print(args)


def test_subparser_conflict():
    pass


@pytest.mark.skip
def test_copy_construct():
    class A:
        def __init__(self):
            self.a = 1

    class B(A):
        def __init__(self, parent):
            self.b = 2
            super().__init__()
            self = parent

    a = A()
    a.a = 10
    b = B(a)
    print(a.a, b.a, b.b)
