# -*- coding: utf-8 -*-

import pytest
from configmate import Config, ConfigException, ConfigLoadException, ConfigLoadFormatException
import os
import yaml
import uuid


MISSING_FILE_NAME = '/file/does/not/exist.yml'
YAML_LOOKUP_FILE_NAME = 'lookup.yml'
YAML_LOOKUP_FILE_DATA = {
    'abc': 'easy as',
    'def': 123
}
YAML_INVALID_DATA_LIST = [
    '---\n',
    '---\nstr\n',
    '---\n123\n',
    '---\ntrue\n',
    '---\nfalse\n',
    '---\n- str\n',
    '---\n- 123\n',
    '---\n- true\n',
    '---\n- false\n',
]


def write_file(file_data, file_name = None, root_dir = None, dump_yaml = False):
    """
    Dump data to a YAML file

    :param file_data: data to dump
    :param file_name: optional file name
    :param root_dir: optional root directory to use, otherwise use current working directory
    :return: absolute name of file
    """

    file_path = file_name or str(uuid.uuid4()) + '.yml'
    file_path = os.path.join(root_dir, file_path) if root_dir else os.path.abspath(file_path)

    with open(file_path, 'w') as file_object:
        if dump_yaml:
            yaml.safe_dump(file_data, file_object, default_flow_style = False)

        else:
            file_object.write(file_data)

    return file_path


def test_error_on_missing_file():
    with pytest.raises(ConfigLoadException):
        Config(config_file_name = MISSING_FILE_NAME)


@pytest.mark.parametrize(
    'invalid_data',
    YAML_INVALID_DATA_LIST
)
def test_error_on_invalid_data(temp_dir, invalid_data):
    with pytest.raises(ConfigLoadException):
        Config(config_string = invalid_data)

    file_name = write_file(invalid_data, root_dir = temp_dir)

    with pytest.raises(ConfigLoadException):
        Config(config_file_name = file_name)


@pytest.mark.parametrize(
    'invalid_data',
    YAML_INVALID_DATA_LIST
)
def test_error_on_including_invalid_data(temp_dir, invalid_data):
    write_file(invalid_data, file_name = 'invalid.yml', root_dir = temp_dir)

    with pytest.raises(ConfigLoadException):
        Config(config_string = invalid_data)

    file_name = write_file('include:\n- invalid.yml', root_dir = temp_dir)

    with pytest.raises(ConfigLoadFormatException):
        Config(config_file_name = file_name)


@pytest.mark.parametrize(
    'invalid_data',
    YAML_INVALID_DATA_LIST
)
def test_error_on_optionally_including_invalid_data(temp_dir, invalid_data):
    write_file(invalid_data, file_name = 'invalid.yml', root_dir = temp_dir)

    with pytest.raises(ConfigLoadFormatException):
        Config(config_string = 'include_optional:\n- invalid.yml')

    file_name = write_file('include_optional:\n- invalid.yml', root_dir = temp_dir)

    with pytest.raises(ConfigLoadFormatException):
        Config(config_file_name = file_name)


def test_including_files(temp_dir):
    file_data = YAML_LOOKUP_FILE_DATA
    write_file(file_data, file_name = YAML_LOOKUP_FILE_NAME, root_dir = temp_dir, dump_yaml = True)

    for include_str in (
        'include:\n- {}\n'.format(YAML_LOOKUP_FILE_NAME),
        'include_optional:\n- {}\n'.format(YAML_LOOKUP_FILE_NAME)
    ):
        config = Config(config_string = include_str)
        assert len(config) == len(file_data.keys())
        for key, val in file_data.iteritems():
            assert config[key] == val

        file_name = write_file(include_str, root_dir = temp_dir)

        config = Config(config_file_name = file_name)
        assert len(config) == len(file_data.keys()) + 1
        assert config['config_file_name'] == file_name
        for key, val in file_data.iteritems():
            assert config[key] == val


def test_including_missing_file(temp_dir):
    file_name = write_file('include_optional:\n- {}'.format(MISSING_FILE_NAME), root_dir = temp_dir)

    config = Config(config_file_name = file_name)
    assert config == {'config_file_name': file_name}


@pytest.mark.parametrize(
    'test_data',
    (
        'include:',
        'include: {}'.format(MISSING_FILE_NAME),
        'include:\n- {}'.format(MISSING_FILE_NAME),
        'include_optional:',
        'include_optional: {}'.format(MISSING_FILE_NAME),
    )
)
def test_error_on_invalid_include(temp_dir, test_data):
    file_name = write_file(test_data, root_dir = temp_dir)

    with pytest.raises(ConfigException):
        Config(config_file_name = file_name)


# TODO test path list
