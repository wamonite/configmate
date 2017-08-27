# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import os
import yaml
import yaml.scanner


def construct_yaml_str(self, node):
    # Override default constructor to skip trying to encode as ASCII first
    return self.construct_scalar(node)


# Replace YAML string constructor to ensure string values returned as unicode
yaml.SafeLoader.add_constructor(u'tag:yaml.org,2002:str', construct_yaml_str)


def read_yaml_file(file_name):
    """
    Read a file as YAML

    :return: None if the file could not be read and parsed
    """

    try:
        with open(file_name, 'r') as file_object:
            return yaml.safe_load(file_object)

    except (IOError, yaml.scanner.ScannerError):
        return None


def read_yaml_string(data):
    """
    Read a string as YAML

    :return: None if the string could not be parsed
    """

    try:
        return yaml.safe_load(data)

    except yaml.scanner.ScannerError:
        return None


def get_path_names(file_name, path_list):
    """
    Return a list of absolute file path

    Construct a list of absolute file paths by adding the file name to the path list values.
    The list will only contain the file name if it is an absolute file path.

    :return: List of absolute file paths
    """

    if file_name and file_name[0] == os.path.sep:
        return [file_name]

    return [os.path.join(path, file_name) for path in path_list]
