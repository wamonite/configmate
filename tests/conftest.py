# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import logging
import pytest
from tempfile import mkdtemp
import os
from shutil import rmtree


LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(name)s %(levelname)s: %(message)s'
LOG_FORMAT_DATE = '%Y-%m-%d %H:%M:%S'


logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)

log_handler = logging.StreamHandler()
log_handler.setLevel(LOG_LEVEL)
logger.addHandler(log_handler)

log_format = logging.Formatter(LOG_FORMAT, datefmt = LOG_FORMAT_DATE)
log_handler.setFormatter(log_format)

log = logging.getLogger('configmate.pytest')


@pytest.fixture()
def temp_dir(request):
    """
    Create a temporary directory and delete after use

    :return: Absolute name of the temporary directory created
    """

    temp_dir_name = mkdtemp(prefix = 'configmate.pytest')
    log.info('created temp dir: {}'.format(temp_dir_name))

    current_dir = os.getcwd()
    os.chdir(temp_dir_name)

    def remove_temp_dir():
        if temp_dir_name:
            log.info('removing temp dir: {}'.format(temp_dir_name))
            rmtree(temp_dir_name)

        os.chdir(current_dir)

    request.addfinalizer(remove_temp_dir)

    return temp_dir_name
