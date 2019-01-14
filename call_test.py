#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  1 16:55:52 2018

@author: dufs
"""

import sshclient as sshClt
import decodepasswd as decp
import hostinfo


if __name__ == "__main__":
    
    hostSet=set()
    hostSet.add(('10.102.52.8', 22444, 'iss', 'Iss@52.8!', 100))
    hostSet.add(('10.102.52.9', 22444, 'iss', 'Iss@52.8!', 101))
    hostSet.add(('10.102.52.10', 22444, 'iss', 'Iss@52.8!', 102))
    hostSet.add(('10.102.52.11', 22444, 'iss', 'Iss@52.8!', 103))
    hostSet.add(('10.102.52.12', 22444, 'iss', 'Iss@52.8!', 104))
    hostSet.add(('10.102.52.13', 22444, 'iss', 'Iss@52.8!', 105))
    hostSet.add(('10.102.52.16', 22444, 'iss', 'Iss@52.8!', 106))
    hostSet.add(('10.102.52.18', 22444, 'iss', 'Iss@52.8!', 107))
    hostSet.add(('10.102.52.19', 22444, 'iss', 'Iss@52.8!', 108))
    hostSet.add(('10.102.52.20', 22444, 'iss', 'Iss@52.8!', 109))
    hostSet.add(('10.102.52.21', 22444, 'iss', 'Iss@52.8!', 110))

    cmdSet=set()
    cmdSet.add(('disk', 'df -k'))
    cmdSet.add(('mem', 'free -m'))
    cmdSet.add(('vmstat', 'vmstat 1 5'))
    cmdSet.add(('ps', 'ps -fu iss'))  
    
    #result=sshClt.ssh_batch_cmd(hostSet, cmdSet)
    #for res in result:
    #    print res
    
    #decpass=decp.DecodePassword()
    #res=decpass.getdecodePassword('GaE+arhkPtNsGdsQOej3hw==', 'dWx0cmEtc3RhY2s=')
    #decpass.shutdownJVM()
    #print res
    
    res=hostinfo.get_hostinfo()
    print res
    
