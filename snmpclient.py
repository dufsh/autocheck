#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 28 12:34:00 2018

@author: dufs
"""

import sys
import time
import netsnmp
import commands
import logging
import logging.config
import ConfigParser
import multiprocessing
import databaseconn as dbcn


#logging.config.fileConfig('conf/logging.conf')
#logger = logging.getLogger(__name__)

logger = logging.getLogger('autocheck.snmpclient')


def snmp_query(host, oid, version=2):
    """
    snmpwalk
    """
    dev_ip=host[0]
    community=host[1]
        
    if oid[1]=='snmpdf':
        try:
            if version==2:
                v_version="2c"
            else:
                v_version=str(version)
            result = commands.getoutput("snmpdf -v " + v_version + " -c " + community + " " + dev_ip)
            logger.debug('exec snmpdf result: %s', str(result))
            result=tuple(result.split('\n'))
            status = 0
            
        except Exception as e:
            logger.error('get Exception : ' + str(e) , exc_info=True)
            result = None
            status = -1
    else:
        try:
            result = netsnmp.snmpwalk(oid[1], Version=version, DestHost=dev_ip, Community=community)
            logger.debug('exec snmpwalk oid[1] result: %s', str(result))
            result = tuple(result)
            status = 0
        except Exception, err:
            logger.error('get Exception : ' + str(e) , exc_info=True)
            result = None
            status = -1
    return (host, oid, status, result)


def snmp_result(res):
    '''
    '''
    if res[2]==0:
        logger.debug("%s exec command '%s' success." %(res[0][0], res[1][1]))
    else:
        logger.debug("%s exec command '%s' failed." %(res[0][0], res[1][1]))
    
    snmp_resultSet.add(res)


def snmp_result_save(resSet):
    '''
    '''
    if len(resSet)==0:
        return
    
    saveSet=set()
    
    for res in resSet:
        IP_ADDRESS=res[0][0]
        DEVICE_ID=res[0][2]
        oid=res[1][1]
        status=res[2]
        result=res[3]
        if status!=0:
            continue
        if len(result)==0:
            continue
        if oid=='ssCpuIdle':
            INSPECTION_INDEX='CPU_UTILIZATION'
            INSPECTION_OBJECT='cpu'
            INDEX_VALUE=100-int(result[0])
            TOTAL=''
            USED=''
            saveSet.add((IP_ADDRESS, DEVICE_ID, INSPECTION_INDEX, INSPECTION_OBJECT, INDEX_VALUE, TOTAL, USED))
        elif oid=='memTotalReal':
            INSPECTION_INDEX='MEM_UTILIZATION'
            INSPECTION_OBJECT=''
            INSPECTION_OBJECT='Mem'
            INDEX_VALUE=''
            TOTAL=int(result[0])
            USED=''
            for res1 in resSet:
                if IP_ADDRESS==res1[0][0] and DEVICE_ID==res1[0][2] and res1[1][1]=='memAvailReal':
                    USED=TOTAL-int(res1[3][0])
                    INDEX_VALUE=round(100*USED/TOTAL,2)
            saveSet.add((IP_ADDRESS, DEVICE_ID, INSPECTION_INDEX, INSPECTION_OBJECT, INDEX_VALUE, TOTAL, USED))

        elif oid=='snmpdf':
            INSPECTION_INDEX='DISK_UTILIZATION'
            for line in result:
                if line.startswith('Description'):
                    continue
                if len(line.split())>5:
                    INSPECTION_OBJECT=line.split()[0] + ' ' + line.split()[1]
                    INDEX_VALUE=line.split()[5].replace('%','')
                    TOTAL=line.split()[2]
                    USED=line.split()[3] 
                elif len(line.split())==5:
                    INSPECTION_OBJECT=line.split()[0]
                    INDEX_VALUE=line.split()[4].replace('%','')
                    TOTAL=line.split()[1]
                    USED=line.split()[2]
                else:
                    continue
                saveSet.add((IP_ADDRESS, DEVICE_ID, INSPECTION_INDEX, INSPECTION_OBJECT, INDEX_VALUE, TOTAL, USED))
        
    logger.info('total %d result need to save', len(saveSet))
    if len(saveSet)==0:
        return 0

    v_sql='''insert into isp_autoinspection_test(ip_address,device_id,inspection_index,inspection_object,index_value,total,used,inspection_time,into_time) values(:x1, :x2, :x3, :x4, :x5, :x6, :x7, trunc(sysdate,'hh24'), sysdate)'''
    logger.info('exec result save sql : %s', v_sql)

    try:
        cf = ConfigParser.SafeConfigParser()
        cf.read('conf/autocheck.conf')
        db_url=cf.get('db', 'url')
        nls_lang=cf.get('db', 'nls_lang')
    except Exception as e:
        logger.error('parse config file error: ' + str(e) , exc_info=True)
        raise

    if len(nls_lang)==0:
        nls_lang='SIMPLIFIED CHINESE_CHINA.UTF8'

    try:
        dbclt=dbcn.DataBaseConn(db_url, nls_lang=nls_lang)
    except Exception as e:
        logger.error('connect db faild : ' + str(e) , exc_info=True)
        return -1
       
    for rlst in saveSet:
        try:
            dbclt.exec_sql(v_sql, rlst)
        except Exception as e:
            logger.error('connect db faild : ' + str(e) , exc_info=True)
    dbclt.conn.commit()
    dbclt.close_connect()
    logger.info('save result success')
        

def snmp_batch_cmd(hostSet, oidSet):
    '''
    '''
    global snmp_resultSet
    snmp_resultSet=set()
    time_start=time.time()
    max_thread=100

    try:
        cf = ConfigParser.SafeConfigParser()
        cf.read('conf/autocheck.conf')
        max_thread=cf.getint('snmpclient', 'max_thread')
    except Exception as e:
        logger.error('parse config file error: ' + str(e) , exc_info=True)
        logger.debug('use defult : %d', max_thread)

    if len(hostSet)<=max_thread:
        pool_size=len(hostSet)
    else:
        pool_size=max_thread
    
    pool = multiprocessing.Pool(processes=pool_size)
    
    for host in hostSet:
        for oid in oidSet:
            pool.apply_async(snmp_query, (host, oid, ), callback=snmp_result)
    pool.close()
    pool.join()
    
    time_end=time.time()
    time_used=time_end-time_start
    logger.info("all sub-processes done, used time %d s" %time_used)

    snmp_result_save(snmp_resultSet)
    

if __name__ == '__main__':

    logging.config.fileConfig("conf/logging.conf")
    #create logger
    logger = logging.getLogger("snmpclient")

    hostSet=set()
    hostSet.add(('183.222.102.82', 'SNMP_COMMUNITY', 100))
    hostSet.add(('183.222.102.14', 'SNMP_COMMUNITY', 101))

    oidSet=set()
    oidSet.add(('disk', 'snmpdf'))
    oidSet.add(('mem', 'memTotalReal'))
    oidSet.add(('mem', 'memAvailReal'))
    oidSet.add(('cpu', 'ssCpuIdle'))
    
    snmp_batch_cmd(hostSet, oidSet)
