#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on Sat Dec  1 11:47:53 2018

@author: dufs
"""

import time
import logging
import logging.config
import ConfigParser
import paramiko
#import traceback
import multiprocessing
import databaseconn as dbcn


#logging.config.fileConfig('conf/logging.conf')
#logger = logging.getLogger(__name__)
logger = logging.getLogger('autocheck.sshclient')


def sshclient_execmd(host, execmd):

    paramiko.util.log_to_file("log/paramiko.log")
    
    hostname=host[0]
    port=host[1]
    username=host[2]
    password=host[3]
    
    try:
        s = paramiko.SSHClient()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        s.connect(hostname=hostname, port=port, username=username, password=password, timeout=3, compress=True)
        stdin, stdout, stderr = s.exec_command (execmd[1])  
        #stdin.write("Y")
        result=stdout.read()
        s.close()
        logger.debug('get result : %s', str(result))
        return (tuple([host[0], host[1], host[4]]), execmd, 0, result)

    except Exception as e:
        logger.error('get Exception : %s', str(e))
        #traceback.print_exc()
        return (tuple([host[0], host[1], host[4]]), execmd, -1, str(e))


def ssh_result(res):
    '''
    '''
    if res[2]==0:
        logger.debug("%s exec command '%s' success.", res[0][0], res[1][1])
    else:
        logger.debug("%s exec command '%s' failed.", res[0][0], res[1][1])
    
    ssh_resultSet.add(res)


def snmp_result_save(resSet):
    '''
    '''
    if len(resSet)==0:
        return
    
    saveSet=set()
    
    for res in resSet:
        IP_ADDRESS=res[0][0]
        DEVICE_ID=res[0][2]
        cmd=res[1][0]
        status=res[2]
        result=res[3]
        if status!=0:
            continue
        if cmd=='mkmfsinfo':
            INSPECTION_INDEX='DISK_STATUS'
            INSPECTION_OBJECT=''
            INDEX_VALUE=''
            TOTAL=''
            USED=''
            if len(result)==0:
                continue
            for line in result.split('\n'):
                if len(line)==0:
                    continue
                if line.split()[0].startswith('devname'):
                    continue
                else:
                    INSPECTION_OBJECT=line.split()[0]
                    if line.split()[1]=='ACTIVE':
                        INDEX_VALUE=1
                    else:
                        INDEX_VALUE=0
                saveSet.add((IP_ADDRESS, DEVICE_ID, INSPECTION_INDEX, INSPECTION_OBJECT, INDEX_VALUE, TOTAL, USED))
        elif cmd=='userinfo':
            INSPECTION_INDEX='ACCOUNT'
            INSPECTION_OBJECT=''
            INDEX_VALUE=''
            TOTAL=''
            USED=''
            for user in result.split('\n'):
                if len(user)==0:
                    continue
                INSPECTION_OBJECT=user
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
        raise

    for rlst in saveSet:
        try:
            dbclt.exec_sql(v_sql, rlst)
        except Exception as e:
            logger.error('connect db faild : ' + str(e) , exc_info=True)
    dbclt.conn.commit()
    dbclt.close_connect()
    logger.info('save result success')
            
    
def ssh_batch_cmd(hostSet, cmdSet):
    global ssh_resultSet
    ssh_resultSet=set()
    time_start=time.time()

    max_thread=100
    try:
        cf = ConfigParser.SafeConfigParser()
        cf.read('conf/autocheck.conf')
        max_thread=cf.getint('sshclient', 'max_thread')
    except Exception as e:
        logger.error('parse config file error: ' + str(e) , exc_info=True)
        logger.debug('use defult : %d', max_thread)

    if len(hostSet)<=max_thread:
        pool_size=len(hostSet)
    else:
        pool_size=max_thread
    
    pool = multiprocessing.Pool(processes=pool_size)
    
    for host in hostSet:        
        for execmd in cmdSet:
            pool.apply_async(sshclient_execmd, (host, execmd), callback=ssh_result)
    pool.close()
    pool.join()
    
    time_end=time.time()
    time_used=time_end-time_start
    logger.info("all sub-processes done, used time %d s", time_used)

    snmp_result_save(ssh_resultSet)
    

if __name__ == "__main__":

    logging.config.fileConfig("conf/logging.conf")
    #create logger
    logger = logging.getLogger("sshclient")
    
    hostSet=set()
    hostSet.add(('10.102.52.9', 22444, 'iss', 'Iss@52.8!', 101))
    hostSet.add(('10.102.52.10', 22444, 'iss', 'Iss@52.8!', 102))

    cmdSet=set()
    cmdSet.add(('userinfo', '''cat /etc/passwd |awk -F":" '{print $1}' '''))
    cmdSet.add(('mkmfsinfo', "sudo -u root mkmfsinfo -querydisk |awk '{print $1,$8}'"))
    
    ssh_batch_cmd(hostSet, cmdSet)
