#!/usr/bin/python
# coding=utf-8
import socket
import struct
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from multiprocessing import Process,Manager
from multiprocessing import Pool
import re
import threading
# __doc__ = '''
#     example:
#     --db=doc/ip_clean.world.txt --iplistfile=/data/tmp/00/iplist.txt
#     --db=doc/ip_clean.china.txt --iplistfile=/data/tmp/00/iplist.txt
#     '''
__doc__ = '''
    example:
    --db=doc/ip_clean.world.txt --processNum=4 --iplistfile=/data/tmp/00/iplist.txt
    --db=doc/ip_clean.china.txt --processNum=4 --iplistfile=/data/tmp/00/iplist.txt
    '''
class ipsearch:
    def __init__(self, dbfile):
        iplist = []
        f = open(dbfile, buffering=1024*1024*10)
        for line in f:
            list_obj = [p.strip() for p in re.split(",", line) if p]
            iplist.append(list_obj)
        f.close()
        self.iplist = iplist  # 保存ip区域数据库

        self.cachestr = {}  # 缓存

    def ipstrtoInt(self, ipstr):
        """
        ip地址转换为整型
        :param ipstr:  字符窜 ip地址
        :return: 整型
        """
        try:
            return socket.ntohl(struct.unpack("I", socket.inet_aton(str(ipstr)))[0])
        except:
            return 0

    def Searchip(self, ipstr):
        """
        查询ip
        :param ipstr: 字符串ip
        :return: 返回区域
        """

        return self.Searchiparea(self.iplist, self.ipstrtoInt(ipstr))

    def Searchiparea(self, iplist, ipint):
        """
        根据整型ip，查询ip区域
        二分查找算法
        :param iplist: ip查询列表
        :param ipint:
        :return: ip区域
        """
        # 根据整型ip 查询ip区域
        if len(iplist) != 0:
            cen_num = len(iplist)/2
            tlag = iplist[cen_num]  # 本次查找 范围值
            gt_list = iplist[0:cen_num]  # 小于部分
            lt_list = iplist[cen_num+1:]  # 大于部分
        else:
            # print(socket.inet_ntoa(struct.pack('I', socket.htonl(ipint))))  # 打印未命中ip
            return 'none'


        if (long(tlag[0]) <= ipint) and (ipint <= long(tlag[1])):  # 如果查找命中，ip在边界中间
            return tlag[2]  # 返回结果

        elif long(tlag[0]) > ipint:  # 如果目标值小于本次查找
            is_se=self.Searchiparea(gt_list, ipint)  # 递归 小于部分

        elif long(tlag[0]) < ipint:  # 如果目标值大于于本次查找
            is_se=self.Searchiparea(lt_list, ipint)  # 递归 大于部分

        return is_se

    def groupbycountry(self, iplist):
        """
        将ip列表转换为地区计数
        :param iplist:
        :return:
        """
        countryesult = self.dictbycountry(iplist)  # 字典形式


        return self.dicttolist(countryesult)  # 字典转换为list 并排序

    def dicttolist(self, countryesult):
        """

        :param countryesult: 区域 : 计数 字典
        :return: 排序后的列表
        """
        countrylist = countryesult.items()

        return sorted(countrylist, key=self.sortCountry)

    def dictbycountry(self, iplist):
        """
        将ip列表转换为地区计数
        :param iplist:
        :return: 返回字典
        """
        countryesult = {}

        for ipstr in iplist:

            countrystr = self.cachestr.get(ipstr, 'miss')  # 先查缓存
            if countrystr == 'miss':
                countrystr = self.Searchip(ipstr)
                self.cachestr[ipstr] = countrystr  # 保存缓存


            countryesult[countrystr] = countryesult.get(countrystr, 0) + 1  # 字典计数加1



        return countryesult  # 返回结果字典

    def sortCountry(self, country):

        return -country[1]  # 排序为倒序，列表的 1 位置 为排序依据
def main():  # 单线程 main
    if len(sys.argv) != 3:
        print __doc__
        sys.exit()

    dbstr = ''
    ipliststr =''

    for i in range(1, len(sys.argv)):
        if sys.argv[i].startswith('--db='):
            dbstr = sys.argv[i][len('--db='):]
        elif sys.argv[i].startswith('--iplistfile='):
            ipliststr = sys.argv[i][len('--iplistfile='):]


        else:
            print __doc__
            sys.exit()

    s = ipsearch(dbstr)
    # areastr = s.Searchip('223.19.227.103')
    # print(areastr)


    iplist = []
    f = open(ipliststr, buffering=1024*1024)
    for line in f:
        iplist.append(line.strip())

    countrylist = s.groupbycountry(iplist)

    for c in countrylist:
        print ('%s %d' % (c[0], c[1]))  # 打印结果

#
class threadrunner(threading.Thread):  # 多线程执行
    """
    多线程类  -- 性能优化无效
    """
    def __init__(self, dbfile, threadNum, iplist, threadLock, countryDictResult, threadNumcount):
        self.countryDictResult = countryDictResult
        self.ipsearcher = ipsearch(dbfile)
        if len(iplist) < threadNum:
            threadNum = 1
        self.threadNum = threadNum
        self.threadNumcount = threadNumcount
        self.liststep = len(iplist)/threadNum
        self.iplist = iplist

        self.threadLock = threadLock

        threading.Thread.__init__(self)
    def run(self):
        self.threadLock.acquire()  # 锁定 -- 分配任务
        if self.threadNumcount[0] < self.threadNum - 1:
            tasklist = self.iplist[self.threadNumcount[0]*self.liststep:((self.threadNumcount[0]+1)*self.liststep)]
            self.threadNumcount[0] = self.threadNumcount[0] + 1
        else:
            tasklist = self.iplist[self.threadNumcount[0]*self.liststep:]

        self.threadLock.release()  # 解锁 -- 任务分配完，执行解锁

        taskresult = self.ipsearcher.groupbycountry(tasklist)  # 开始查询

        self.threadLock.acquire()  # 锁定 -- 合并结果

        for partcount in taskresult:

            self.countryDictResult[partcount[0]] = self.countryDictResult.get(partcount[0], 0) + partcount[1]

        self.threadLock.release()  # 解锁 -- 合并结果完成

def threadingmain():  # 多线程，python多线程 不能利用多核心cpu，已废弃
    if len(sys.argv) != 4:
        print __doc__
        sys.exit()

    dbstr = ''
    ipliststr =''
    threadNum = 1
    for i in range(1, len(sys.argv)):
        if sys.argv[i].startswith('--db='):
            dbstr = sys.argv[i][len('--db='):]
        elif sys.argv[i].startswith('--iplistfile='):
            ipliststr = sys.argv[i][len('--iplistfile='):]
        elif sys.argv[i].startswith('--threadnum='):
            threadNum = int(sys.argv[i][len('--threadnum='):])

        else:
            print __doc__
            sys.exit()

    s = ipsearch(dbstr)
    # areastr = s.Searchip('223.19.227.103')
    # print(areastr)


    iplist = []
    f = open(ipliststr, buffering=1024*1024)
    for line in f:
        iplist.append(line.strip())

    threadLock = threading.Lock()
    threads = []
    countryDictResult = {}
    threadNumcount = [0]


    for i in range(0, threadNum):
        countThread = threadrunner(dbstr, threadNum, iplist, threadLock, countryDictResult, threadNumcount)
        countThread.setDaemon(True)  # 为了支持ctrl + c
        countThread.start()  # 开始执行
        threads.append(countThread)

    while True:  # 为了支持ctrl + c
        alive = False
        for thread in threads:
            alive = alive or thread.isAlive()
        if not alive:
            break
    # countrylist = s.groupbycountry(iplist)

    countrylist = countryDictResult.items()


    for c in sorted(countrylist, key=ipsearch(dbstr).sortCountry):
        print ('%s %d' % (c[0], c[1]))
# @profile  性能测试
def processmain():  # 多进程
    if len(sys.argv) != 4:
        print __doc__
        sys.exit()

    dbstr = ''  # 数据库文件
    ipliststr =''  # 待查ip
    processNum = 1  # 默认进程数
    for i in range(1, len(sys.argv)):
        if sys.argv[i].startswith('--db='):
            dbstr = sys.argv[i][len('--db='):]
        elif sys.argv[i].startswith('--iplistfile='):
            ipliststr = sys.argv[i][len('--iplistfile='):]
        elif sys.argv[i].startswith('--processNum='):
            processNum = int(sys.argv[i][len('--processNum='):])

        else:
            print __doc__
            sys.exit()

    ipsearcher = ipsearch(dbstr)  # 初始化 查询类
    # areastr = s.Searchip('223.19.227.103')
    # print(areastr)


    iplist = []
    f = open(ipliststr, buffering=1024*1024)
    for line in f:
        iplist.append(line.strip())  # 读入所有待查ip


    p = Pool(processes=processNum)  # 进程池
    manager = Manager()
    results_list = []
    for i in range(0, processNum):
        result_dict = manager.dict()  # 进程间通信 传参字典
        results_list.append(result_dict)  # 每个进程使用一个字典
        p.apply_async(run, [i, ipsearcher, processNum, iplist, result_dict])  # 开始查询，结果存入result_dict

    p.close()
    p.join()  # 进程阻塞，等待全部完成

    result_dict_all = {}  # 最终字典结果
    for result_dict_l in results_list:  # 开始合并，合并每个结果集
        result_list = result_dict_l.items()   # 转换列表 用于循环
        for r in result_list:
            result_dict_all[r[0]] = result_dict_all.get(r[0], 0) + result_dict_l.get(r[0], 0)  # 循环合并

    taskresultlist = ipsearcher.dicttolist(result_dict_all)  # 转换为列表 并排序
    print('result:')  # 输出结果
    for c in taskresultlist:
        print ('%s %d' % (c[0], c[1]))

def run(processNumcount, ipsearcher, processNum, iplist, result_dict):  # 执行函数
    liststep = len(iplist)/processNum  # 根据进程数确定步长
    if processNumcount < processNum - 1:
        tasklist = iplist[processNumcount*liststep:((processNumcount+1)*liststep)]
    else:
        tasklist = iplist[processNumcount*liststep:]
    result_list = ipsearcher.dictbycountry(tasklist).items()   # 开始查询

    # result_dict.update(ipsearcher.dictbycountry(tasklist))
    for r in result_list:

        result_dict[r[0]] = r[1]  # 存入结果字典 只有这个字典可用进程传参


if __name__ == '__main__':
    import time
    starttime = time.time()
    processmain()  # 调用多进程
    stoptime = time.time()  # 查询计时

    print('run time : %d second' % (stoptime - starttime))