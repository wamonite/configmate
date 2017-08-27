# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
from copy import deepcopy
import os
from .file_utils import read_yaml_file, read_yaml_string
from collections import MutableMapping
import logging


log = logging.getLogger('configmate.config')


CONFIG_FILE_NAME_KEY = 'config_file_name'
CONFIG_INCLUDE_KEY = 'include'
CONFIG_INCLUDE_OPTIONAL_KEY = 'include_optional'


class ConfigException(Exception):
    pass


class ConfigLoadException(ConfigException):
    pass


class ConfigLoadFormatException(ConfigLoadException):
    pass


class ConfigFileLoader(object):

    def __init__(self, file_name, path_list = None, initial_config = False):
        self._file_name = file_name
        self._path_list = path_list if path_list else ['']
        self._initial_config = initial_config
        self._loaded_file_list = []

    @property
    def name_list(self):
        return self._loaded_file_list or [self._file_name]

    @property
    def names(self):
        return ', '.join(["'{}'".format(name) for name in self.name_list])

    @property
    def path_list(self):
        return self._path_list

    @property
    def initial_config(self):
        return self._initial_config

    def get_data(self):
        config_data_list = []

        path_list = self._path_list
        if self._initial_config:
            path_list = path_list[:1]

        self._loaded_file_list = []
        for path in reversed(path_list):
            file_name = os.path.join(path, self._file_name)
            config_data = read_yaml_file(file_name)

            if config_data:
                if not isinstance(config_data, dict):
                    raise ConfigLoadFormatException(
                        "Config file should contain a valid YAML dictionary: '{}'".format(
                            file_name
                        )
                    )

                config_data_list.append(config_data)
                self._loaded_file_list.append(file_name)

        if not config_data_list:
            raise ConfigLoadException(
                "Unable to load config: '{}'".format(
                    self._file_name
                )
            )

        return config_data_list


class ConfigStringLoader(object):

    CONFIG_NAME = '<string>'

    def __init__(self, config_string, path_list = None, initial_config = False):
        self._config_string = config_string
        self._path_list = path_list
        self._initial_config = initial_config

    @property
    def name_list(self):
        return [self.CONFIG_NAME]

    @property
    def names(self):
        return self.CONFIG_NAME

    @property
    def path_list(self):
        return self._path_list

    @property
    def initial_config(self):
        return self._initial_config

    def get_data(self):
        config_data = read_yaml_string(self._config_string)
        if config_data is None:
            raise ConfigLoadException(
                "Unable to load config: {}".format(
                    self.CONFIG_NAME
                )
            )

        if not isinstance(config_data, dict):
            raise ConfigLoadFormatException(
                "Config file should contain a valid YAML dictionary: {}".format(
                    self.CONFIG_NAME
                )
            )

        return [config_data]


class Config(MutableMapping):

    def __init__(
            self,
            config_file_name = None,
            config_string = None,
            path_list = None,
            defaults = None
    ):
        self._path_list = path_list

        if defaults and not isinstance(defaults, dict):
            raise ConfigException('Config defaults must be a dict')
        self._config = deepcopy(defaults) if defaults else {}

        self._uuid_cache = {}

        if config_file_name is not None:
            self._config[CONFIG_FILE_NAME_KEY] = config_file_name
            config_loader = ConfigFileLoader(config_file_name, path_list = path_list, initial_config = True)
            self._read_config(config_loader)

        if config_string is not None:
            config_loader = ConfigStringLoader(config_string, path_list = path_list, initial_config = True)
            self._read_config(config_loader)

    def expand_parameter(self, value):
        # TODO process values
        return value

    def __getitem__(self, key):
        if key in self._config:
            return self.expand_parameter(self._config[key])

        raise KeyError("'" + key + "'")

    def __setitem__(self, key, value):
        self._config[key] = value

    def __delitem__(self, key):
        if key in self._config:
            del self._config[key]

        else:
            raise KeyError("'" + key + "'")

    def __iter__(self):
        return iter(self._config)

    def __len__(self):
        return len(self._config)

    def _read_config(self, config_loader):
        self._read_config_core(config_loader)

        if config_loader.initial_config:
            log.info("Loaded config: %s", config_loader.names)

        for config_data in config_loader.get_data():
            self._read_config_includes(CONFIG_INCLUDE_KEY, config_data, config_loader)
            self._read_config_includes(CONFIG_INCLUDE_OPTIONAL_KEY, config_data, config_loader, optional = True)

    def _read_config_core(self, config_loader):
        config_data_list = config_loader.get_data()

        for config_data in config_data_list:
            if 'include' in config_data:
                del(config_data['include'])

            if 'include_optional' in config_data:
                del(config_data['include_optional'])

            self._config.update(config_data)

    def _read_config_includes(self, include_key, config_data, config_loader, optional = False):
        if include_key in config_data:
            if not isinstance(config_data[include_key], list):
                raise ConfigLoadFormatException(
                    "Config file {}includes should contain a valid YAML list: {}".format(
                        'optional ' if optional else '',
                        config_loader.names
                    )
                )

            for include_file_name in config_data[include_key]:
                include_file_name_full = self.expand_parameter(include_file_name)
                try:
                    include_config_loader = ConfigFileLoader(
                        include_file_name_full,
                        path_list = config_loader.path_list
                    )
                    self._read_config(include_config_loader)

                except ConfigLoadFormatException:
                    raise

                except ConfigLoadException:
                    if optional:
                        log.debug("Skipped optional config: '%s'", include_file_name_full)

                    else:
                        raise

                else:
                    if optional:
                        log.info(
                            "Included optional config: %s into %s",
                            include_config_loader.names,
                            config_loader.names
                        )

    def __str__(self):
        return unicode(self).decode('utf-8')

    def __unicode__(self):
        return unicode(self._config)

    def __repr__(self):
        return "{}(\n{}\n)".format(
            self.__class__.__name__,
            str(self)
        )
