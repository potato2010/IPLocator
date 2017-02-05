#!/usr/bin/python
# coding=utf-8
import socket
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import struct

def dbinit(redis_store):
    # 数据库初始化
    pipe = redis_store.pipeline()
    country_word = open('doc/country.world.txt', buffering=1024*1024*30)   # 30MB 缓存
    iplist_word = open('doc/ip_clean.world.txt', buffering=1024*1024*30)   # 30MB 缓存

    # =====================================================
    # 初始化区域字典 country.world:num (num 为数字)
    # linelist = []
    # for line in country_word:
    #     linestr = line.strip()
    #     linelist.append(linestr)
    #
    # for i in range(0, len(linelist)):
    #     pipe.set("country.world:%d" % i, linelist[i])
    # resultlist = pipe.execute()
    # 测试一条数据
    # pipe.get("country.world:%d" % i)
    # 导入国家字典结束 -- 性能没问题的话，可省略

    # =========================================================

    pipe.zrangebyscore('ip.world', 0, 0, start=0, num=1)
    resultlist = pipe.execute()
    if len(resultlist[0]) != 0:  # 取不到值，则证明
        country_word.close()
        iplist_word.close()
        return False

    # print(resultlist)
    for ipitem in iplist_word:
        ip_obj_list = ipitem.strip().split(',')
        pipe.zadd('ip.world', '%s,%s' % (ip_obj_list[0], ip_obj_list[2]), int(ip_obj_list[1]))
    resultlist = pipe.execute()
    # print(resultlist)
    country_word.close()
    iplist_word.close()

    return True

def redissearchip(ipint, redis_store):
    pipe = redis_store.pipeline()
    pipe.zrangebyscore('ip.world', ipint, '+inf', start=0, num=1)
    resultlist = pipe.execute()
    print(resultlist)

def ipstrtoInt(ipstr):
    """
    ip地址转换为整型
    :param ipstr:  字符窜 ip地址
    :return: 整型
    """
    try:
        return socket.ntohl(struct.unpack("I", socket.inet_aton(str(ipstr)))[0])
    except:
        return 0

def sortCountry(country):

    return -country[1]  # 排序为倒序，列表的 1 位置 为排序依据

def getipintlistfromFile(filepath):

    ipintlist = []  # 存储所有整型ip信息
    for ipstr in open(filepath, buffering=512*1024):
        ipint = ipstrtoInt(ipstr.strip())
        ipintlist.append(ipint)

    return ipintlist
def searchiplist(ipintlist, redis_store):
    # 批量查询 优化速度

    resultlist = []
    pipe = redis_store.pipeline()
    for ipint in ipintlist:
        pipe.zrangebyscore('ip.world', ipint, '+inf', start=0, num=1)

    rawresultlist = pipe.execute()

    for i in range(0, len(ipintlist)):
        iprawlist = rawresultlist[i][0].split(',')
        if iprawlist[0] >= ipintlist[i]:
            resultlist.append(iprawlist[1])
        else:
            resultlist.append('none')

    return resultlist

def getresultdict(resultlist):
    countryesult = {}
    for countrystr in resultlist:
        countryesult[countrystr] = countryesult.get(countrystr, 0) + 1

    return countryesult

def dicttolist(countryesult):
    """

    :param countryesult: 区域 : 计数 字典
    :return: 排序后的列表
    """
    countrylist = countryesult.items()

    return sorted(countrylist, key=sortCountry)


def main():

    starttime = time.time()
    # dbinit()
    # redissearchip(0)
    ipintlist = getipintlistfromFile('/home/wz/netstat3.txt')
    rawresultlist = searchiplist(ipintlist)
    resultdict = getresultdict(rawresultlist)
    resultlist = dicttolist(resultdict)

    stoptime = time.time()  # 查询计时

    print('run time : %d second' % (stoptime - starttime))


    for c in resultlist:
        print ('%s %d' % (c[0], c[1]))

if __name__ == '__main__':
    main()