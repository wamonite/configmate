# -*- coding: utf-8 -*-

import pytest
from configmate import Config, ConfigException, ConfigLoadException
import os
import yaml


MISSING_FILE_NAME = '/file/does/not/exist.yml'
YAML_CONFIG_FILE_NAME = 'config.yml'
YAML_LOOKUP_FILE_NAME = 'lookup.yml'
YAML_LIST_FILE_NAME = 'list.yml'
YAML_FILE_DATA = {
    YAML_CONFIG_FILE_NAME: {
        'fizz': 'abc',
        'buzz': 'def'
    },
    YAML_LOOKUP_FILE_NAME: {
        'abc': 'easy as',
        'def': 123
    },
    YAML_LIST_FILE_NAME: [
        '456',
        'ghi'
    ]
}


@pytest.fixture()
def yaml_file_lookup(temp_dir):
    file_name_lookup = {}
    for file_name, file_data in YAML_FILE_DATA.iteritems():
        file_name_full = os.path.join(temp_dir, file_name)
        file_name_lookup[file_name] = file_name_full

        with open(file_name_full, 'w') as file_object:
            yaml.safe_dump(file_data, file_object, default_flow_style = False)

    os.chdir(temp_dir)

    return file_name_lookup


@pytest.fixture()
def config_with_files(yaml_file_lookup):
    return Config(config_file_name = yaml_file_lookup[YAML_CONFIG_FILE_NAME])


def test_config_file_missing():
    with pytest.raises(ConfigLoadException):
        Config(config_file_name = MISSING_FILE_NAME)


@pytest.mark.parametrize(
    'include_str',
    (
        'include_optional:\n- {MISSING_FILE_NAME}',
        'include:\n- {YAML_LOOKUP_FILE_NAME}',
        'include_optional:\n- {YAML_LOOKUP_FILE_NAME}',
    )
)
def test_config_file_include(yaml_file_lookup, include_str):
    config_file_name = yaml_file_lookup[YAML_CONFIG_FILE_NAME]
    with open(config_file_name, 'a') as file_object:
        file_object.write(include_str.format(**(globals())))

    Config(config_file_name = config_file_name)


@pytest.mark.parametrize(
    'include_str',
    (
        'include:',
        'include: {MISSING_FILE_NAME}',
        'include:\n- {MISSING_FILE_NAME}',
        'include_optional:',
        'include_optional: {MISSING_FILE_NAME}',
        'include:\n- {YAML_LIST_FILE_NAME}',
        'include_optional:\n- {YAML_LIST_FILE_NAME}',
    )
)
def test_config_file_include_errors(yaml_file_lookup, include_str):
    config_file_name = yaml_file_lookup[YAML_CONFIG_FILE_NAME]
    with open(config_file_name, 'a') as file_object:
        file_object.write(include_str.format(**(globals())))

    with pytest.raises(ConfigException):
        Config(config_file_name = config_file_name)


def test_config_include_missing():
    with pytest.raises(ConfigLoadException):
        Config(config_file_name = MISSING_FILE_NAME)


def test_config_files(config_with_files):
    for key, value in YAML_FILE_DATA[YAML_CONFIG_FILE_NAME].iteritems():
        assert config_with_files[key] == value
