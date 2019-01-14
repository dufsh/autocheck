#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 28 12:34:00 2018

@author: dufs
"""

import os
import cx_Oracle
import logging
import logging.config


logging.config.fileConfig('conf/logging.conf')
logger = logging.getLogger(__name__)


class DataBaseConn():
    '''
    '''

    def __init__(self, url, nls_lang='SIMPLIFIED CHINESE_CHINA.UTF8'):
        self.url=url

        try:
            os.environ['NLS_LANG'] = nls_lang
            self.conn=cx_Oracle.connect(self.url)
        except Exception as e:
            logger.error('get connect faild : ' + str(e) , exc_info=True)
            raise

    def close_connect(self):
        self.conn.close()

    def exec_sql(self, sql, *argList):
        # sql
        
        try:
            if not isinstance(sql,basestring):
                logger.error('sql is not a string ', exc_info=True)
                raise
            else:
                #logger.info('get exec sql =  %s ' , sql)
                self.curs=self.conn.cursor()
                if argList:
                    logger.debug('get exec sql argList : %s', str(argList))
                    result=self.curs.execute(sql, argList[0])
                else:
                    result=self.curs.execute(sql)
                self.conn.commit()
                #logger.info('exec sql success')
                return result
        except Exception:
            logger.error('execInsertSql faild : ' , exc_info=True)
            raise
