#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  3 23:30:49 2018

@author: dufs
"""

import logging.config
import hostinfo as hf
import sshclient as sshcl

if __name__ == '__main__':

    logging.config.fileConfig("conf/logging.conf")
    #create logger
    logger = logging.getLogger("autocheck")
    
    hostList=hf.get_hostinfo()
    if hostList[0]!=0:
        logger.error('get hostinfo error')
        raise
    
    hostSet=set()
    for host in hostList[1]:
        if host[3] is None or len(host[3])==0 or host[4] is None or len(host[4])==0:
            continue
        hostSet.add((host[1], int(host[2]), host[3], host[4], host[0]))
    
    logger.info('get host number %d', len(hostSet))
    if len(hostSet)>0:
        cmdSet=set()
        cmdSet.add(('userinfo', '''cat /etc/passwd |awk -F":" '{print $1}' '''))
        cmdSet.add(('mkmfsinfo', "sudo -u root mkmfsinfo -querydisk |awk '{print $1,$8}'"))

        sshcl.ssh_batch_cmd(hostSet, cmdSet)
    logger.info('exec autocheck_day finished')
