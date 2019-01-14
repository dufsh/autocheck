#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 15:28:17 2018

@author: dufs
 id ip_address port account password pwdkey
"""

import logging.config
import ConfigParser
import decodepasswd as decpwd
import databaseconn as dbcn

#logging.config.fileConfig('conf/logging.conf')
#logger = logging.getLogger(__name__)
logger = logging.getLogger('autocheck.hostinfo')


def get_hostinfo(if_decodepasswd=True):
    '''
    '''

    try:
        cf = ConfigParser.SafeConfigParser()
        cf.read('conf/autocheck.conf')
        db_url=cf.get('db', 'url')
        nls_lang=cf.get('db', 'nls_lang')
    except Exception as e:
        logger.error('parse config file error: ' + str(e) , exc_info=True)
        return [-1, ]

    if len(nls_lang)==0:
        nls_lang='SIMPLIFIED CHINESE_CHINA.UTF8'
    
    v_sql='''select id,ip_address,nvl(port,0),nvl(account,''),nvl(password,''),nvl(pwdkey,'') from isp_autoinspection_device where ip_address is not null'''
    
    try:
        dbclt=dbcn.DataBaseConn(db_url, nls_lang=nls_lang)
    except Exception as e:
        logger.error('connect db faild : ' + str(e) , exc_info=True)
        return [-1, ]
    try:
        v_set=set()
        res=dbclt.exec_sql(v_sql)
        #logger.info('get hostinfo total %d', len(res))

        if if_decodepasswd==True:
            dp=decpwd.DecodePassword()
        for dev_id, dev_ip, port, account, password, pwdkey in res:
            logger.debug("id = %s, ip = %s, port = %d, account = %s, password = %s, pwdkey = %s" % (dev_id, dev_ip, int(port), account, password, pwdkey))
            if if_decodepasswd==True:
                desPass=dp.getdecodePassword(password, pwdkey)
            else:
                desPass=password
            v_set.add(tuple([dev_id, dev_ip, port, account, desPass]))
            #logger.debug("id = %s, ip = %s, port = %d, account = %s, password = %s" % (dev_id, dev_ip, int(port), account, desPass))
        return [0, v_set]
    except Exception as e:
        logger.error('get Exception : ' + str(e) , exc_info=True)
        return [-99, ]
    
    finally:
        dbclt.close_connect()

