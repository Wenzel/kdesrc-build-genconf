#!/usr/bin/env python3

"""
Usage:
    test_parser.py [options] <configfile>

options:
    -h --help           Show this screen.
    --version           Show version.
"""


import sys
import os
import docopt
import logging

from Config import ConfigFile

def init_logger():
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)

def main(cmdline):
    init_logger()
    conf = ConfigFile(cmdline['<configfile>'])
    conf.load()

if __name__ == '__main__':
    cmdline = docopt.docopt(__doc__)
    excode = main(cmdline)
    sys.exit(excode)