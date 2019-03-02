#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import yaml

from src import main

import logging.config

if __name__ == '__main__':
    # logging configurations
    logging_cfg = yaml.load(open('logging.conf.yaml'))
    loglevel = os.environ.get('LOGLEVEL', 'INFO')
    logging_cfg['loggers']['src']['level'] = loglevel

    logging.config.dictConfig(logging_cfg)

    main()