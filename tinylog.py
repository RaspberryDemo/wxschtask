#!/usr/local/bin/python
# -*- coding:utf-8 -*-
import logging

def glog(logname, logfile):
    logger = logging.getLogger(logname)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.DEBUG)
    fmt = "%(asctime)-15s %(levelname)s %(filename)s %(lineno)d %(process)d %(message)s"
    datefmt = "%a %d %b %Y %H:%M:%S"
    formatter = logging.Formatter(fmt, datefmt)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger

if __name__ == '__main__':
    logger = glog(__name__, './tinylog.log')
    logger.warn('hello world')
    logger.warn('welcome back')
