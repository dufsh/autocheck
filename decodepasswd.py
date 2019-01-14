#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 15:28:17 2018

@author: dufs
 decode password  by key
"""

import os
import logging
import logging.config
import jpype
import os.path


#logging.config.fileConfig('conf/logging.conf')
#logger = logging.getLogger(__name__)
logger = logging.getLogger('autocheck.decodepasswd')


class DecodePassword():
    '''
    '''
    def __init__(self):
        jarpath =os.path.join(os.path.abspath('.'),'./')
        jvmpath=jpype.getDefaultJVMPath()
        #jvmpath='/Library/Java/JavaVirtualMachines/jdk1.8.0_131.jdk/Contents/Home/jre/lib/server/libjvm.dylib'
        if jpype.isJVMStarted()>0:
            jpype.shutdownJVM()
        else:
            jpype.startJVM(jvmpath, "-ea", "-Djava.class.path=%s" % (jarpath + "testP.jar"))
        self.Jcls = jpype.JPackage("com.zznode.utils").DESDecryptCoder()
    
    def getdecodePassword(self, passwd, key):
        '''
        '''
        if passwd is None or key is None:
            desPass=''
        else:
            desPass=self.Jcls.decrypt(passwd, key)
        logger.debug("enPass = %s , desPass = %s" % (passwd, desPass))
        return desPass
    
    def shutdownJVM(self):
        jpype.shutdownJVM()


if ( __name__ == "__main__"):
    
    logging.config.fileConfig("conf/logging.conf")
    #create logger
    logger = logging.getLogger("decodepassword")
    decpass=DecodePassword()
    decpass.getdecodePassword('GaE+arhkPtNsGdsQOej3hw==', 'dWx0cmEtc3RhY2s=')
    decpass.shutdownJVM()
