#!/usr/bin/python
# coding=utf-8
import re
import socket
import struct

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

__doc__ = '''
    example:
    --in=doc/ip.txt --out=doc/ip_clean.world.txt --group=doc/country.world.txt
    --in=doc/ip.txt --out=doc/ip_clean.china.txt --group=doc/country.china.txt
    '''

class cleaniplist:

    def __init__(self, groupstr):
        f = open(groupstr)
        self.contrylist = []
        for i in f:
                self.contrylist.append(i.strip())  # 添加可用国家或地区名单

    def cleanip(self, sourcefile='ip.txt', targetfile='ip_clean.txt'):
        """
        根据原始ip库文件，整理生成精简ip地址库
        :param sourcefile: 清理源文件
        :param targetfile: 清理后的目标文件
        :return:
        """

        # print(self.contrylist)

        buffsize = 1024*1024*30  # 30MB 缓存
        fw = open(targetfile, 'w', buffering=buffsize)

        ipholder = ipchecker('10.0.0.0', '10.255.255.255', u'A类私网')  # 第一个对比参数

        for line in open(sourcefile, 'r', buffering=buffsize):  # 遍历原始ip地址库文件

            list_obj = [p.strip() for p in re.split("\t", line) if p]
            # print(list_obj[2])


            for keyword in self.contrylist:
                if list_obj[2].find(keyword) >= 0:
                    # print("%s,%s,%s" % (list_obj[0], list_obj[1], keyword))

                    ipholdernext = ipchecker(list_obj[0], list_obj[1], keyword)  # 初始化下一个ip地址

                    booleanresult = ipholder.checkafter(ipholdernext)  # 两个ip地址对比，如果可连接则返回true

                    if ipholder.ipstop == ipholdernext.ipstop:  # ip终止点重复，不进行连接
                        continue
                    elif booleanresult:  # 可以连接
                        ipholder.ipstop = ipholdernext.ipstop  # 扩展
                    else:  # 不可连接 ipholder.ipstrtoInt()
                        # 上一组ip 写入 ip地址用整形表示
                        # 下一组ip 放入待连接ipholder
                        fw.write("%s,%s,%s\n" % (ipholder.ipstrtoInt(ipholder.ipstart), ipholder.ipstrtoInt(ipholder.ipstop), ipholder.area))
                        ipholder = ipholdernext

        fw.write("%s,%s,%s\n" % (ipholder.ipstrtoInt('172.16.0.0'), ipholder.ipstrtoInt('172.31.255.255'), u'B类私网'))
        fw.write("%s,%s,%s\n" % (ipholder.ipstrtoInt('192.168.0.0'), ipholder.ipstrtoInt('192.168.255.255'), u'C类私网'))
        fw.write("%s,%s,%s\n" % (ipholder.ipstrtoInt('0.0.0.0'), ipholder.ipstrtoInt('0.0.0.0'), u'本机'))
        fw.write("%s,%s,%s\n" % (ipholder.ipstrtoInt('127.0.0.1'), ipholder.ipstrtoInt('127.0.0.1'), u'本机'))
        fw.close()

        iplist = []
        f = open(targetfile, buffering=buffsize)  # 读取写入的文件
        for line in f:
            list_obj = [p.strip() for p in re.split(",", line) if p]
            iplist.append(list_obj)
        f.close()

        f = open(targetfile, 'w', buffering=buffsize)
        iplist.sort()

        for ipobj in sorted(iplist, key=self.intstart):  # 排序后重新写入
            f.write('%s,%s,%s\n' % (ipobj[0], ipobj[1], ipobj[2]))

        f.close()

    def intstart(self, iplist):  # 转为整型
        return long(iplist[0])

class ipchecker:

    def __init__(self, ipstart, ipstop, area):
        self.ipstart = ipstart  # ip起点
        self.ipstop = ipstop  # ip终点
        self.area = area  # 区域名称

    def checkafter(self, ipchecker):

        c1 = (self.ipstrtoInt(self.ipstop) +1) == self.ipstrtoInt(ipchecker.ipstart)  # ip是否连续

        if ipchecker.area == u'中国':  # 区域分布 中国 不合法 强制设为 区域可合并，这个并不严谨，但是大部分情况是正确的
            c2 = True
        else:
            c2 = (self.area == ipchecker.area)  # 区域名称一致，可连接

        if c1 and c2:  # 如果ip可连接 并且 区域可连接
            return True

        else:
            return False


    def ipstrtoInt(self, ipstr):  # 将ip地址转为整型

        return socket.ntohl(struct.unpack("I",socket.inet_aton(str(ipstr)))[0])

def main():

    if len(sys.argv) != 4:
        print __doc__
        sys.exit()

    instr = ''  # 输入文件 原始ip地址库
    outstr =''  # 输出文件
    groupstr = ''  # 区域和国家 分类文件

    for i in range(1, len(sys.argv)):
        if sys.argv[i].startswith('--in='):
            instr = sys.argv[i][len('--in='):]
        elif sys.argv[i].startswith('--out='):
            outstr = sys.argv[i][len('--out='):]
        elif sys.argv[i].startswith('--group='):
            groupstr = sys.argv[i][len('--group='):]

        else:
            print __doc__
            sys.exit()

    c = cleaniplist(groupstr)  # 初始化分类器

    c.cleanip(instr, outstr)  # 开始分类

if __name__ == '__main__':


    main()