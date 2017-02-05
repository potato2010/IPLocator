#!/usr/bin/python
# coding=utf-8
import socket
import struct
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from search import *
if __name__ == '__main__':
    import time
    starttime = time.time()
    processmain()
    stoptime = time.time()

    print('run time : %d second' % (stoptime - starttime))