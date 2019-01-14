#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  3 17:40:17 2018

@author: dufs
"""

import sys
import logging.config
import hostinfo as hf
import snmpclient as scl

if __name__ == '__main__':

    logging.config.fileConfig("conf/logging.conf")
    #create logger
    logger = logging.getLogger("autocheck")
    
    hostList=hf.get_hostinfo(False)
    if hostList[0]!=0:
        logger.error('get hostinfo error')
        raise
    
    hostSet=set()
    for host in hostList[1]:
        hostSet.add((host[1], 'SNMP_COMMUNITY', host[0]))
    
    logger.info('get host number %d', len(hostSet))
    if len(hostSet)>0:
        oidSet=set()
        oidSet.add(('disk', 'snmpdf'))
        oidSet.add(('mem', 'memTotalReal'))
        oidSet.add(('mem', 'memAvailReal'))
        oidSet.add(('cpu', 'ssCpuIdle'))
        scl.snmp_batch_cmd(hostSet, oidSet)
    logger.info('exec autocheck_hour finished')
