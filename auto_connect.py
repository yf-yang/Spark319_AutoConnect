#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

from src import main

import logging.config

# logging configurations
logging_cfg = { 
    'disable_existing_loggers': True,
    'formatters': { 
        'consoleFormatter': { 
            'class': 'logging.Formatter',
            'format': '%(levelname)s %(filename)s:%(lineno)d %(message)s'
        },
        'fileFormatter': { 
            'class': 'logging.Formatter',
            'datefmt': '%Z %x-%X',
            'format': '%(asctime)s,%(msecs)03d %(levelname)8s '
                '%(filename)s:%(lineno)d %(message)s'
        },
    },
    'handlers': { 
        'consoleHandler': { 
            'class': 'logging.StreamHandler',
            'formatter': 'consoleFormatter',
            'level': 'DEBUG',
            'stream': 'ext://sys.stdout'
        },
        'fileHandler': { 
            'class': 'logging.FileHandler',
            'filename': '/tmp/auto_connect.log',
            'formatter': 'fileFormatter',
            'level': 'DEBUG',
            'mode': 'a'
        }
    },
    'loggers': {
        'src': {
            # 'handlers': ['fileHandler'],
             'handlers': ['fileHandler', 'consoleHandler']
        }
    },
    'version': 1
}

if __name__ == '__main__':
    loglevel = os.environ.get('LOGLEVEL', 'INFO')
    logging_cfg['loggers']['src']['level'] = loglevel

    logging.config.dictConfig(logging_cfg)

    main()
