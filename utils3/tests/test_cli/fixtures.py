import pytest

config_text = (
    'a=1\n'

    'a.b.c=1\n'
    'dot.a.b.c=1\n'
    'a_b_c=1\n'

    'int=1\n'
    'list=[1]\n'
    'dict={"1":1}\n'
    'str=1'
)


@pytest.fixture()
def config_file(tmp_path):
    file = tmp_path / 'default.config'
    file.write_text(config_text)
    return file


@pytest.fixture()
def section_config_file(tmp_path):
    file = tmp_path / 'default.config'
    file.write_text('[DEFAULT]\n' + config_text)
    return file


@pytest.fixture()
def parsed_config(section_config_file):
    pass


@pytest.fixture()
def parsed_args():
    pass
