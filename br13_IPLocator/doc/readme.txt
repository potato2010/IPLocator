
注意：docker 启动不要看此文档

1、生成数据库

下载纯真数据库，提取 qqwry.dat 文件 http://update.cz88.net/soft/setup.zip
放入doc目录下 doc/qqwry.dat

生成ip数据
cd /data/tools/br13_IPLocator/doc
/data/tools/python2.7/bin/python2.7 qqwry.py --dump -o ip.txt

生成中国与世界级别数据
cd /data/tools/br13_IPLocator
/data/tools/python2.7/bin/python2.7 main_createdb.py --in=doc/ip.txt --out=doc/ip_clean.world.txt --group=doc/country.world.txt
/data/tools/python2.7/bin/python2.7 main_createdb.py --in=doc/ip.txt --out=doc/ip_clean.china.txt --group=doc/country.china.txt

清理redis
#select 0 切换到数据库0
#keys * ，看所有key
#flushdb:删除这个db下的key
#flushall:删除所有


访问接口，初始化redis
http://172.16.2.40:9013/init

测试ip
http://172.16.2.40:9013/singleip?ip=123.207.174.172


2、查询

/data/tools/python2.7/bin/python2.7 main_search.py --db=doc/ip_clean.world.txt --iplistfile=/data/tmp/00/iplist.txt
/data/tools/python2.7/bin/python2.7 main_search.py --db=doc/ip_clean.china.txt --iplistfile=/data/tmp/00/iplist.txt
