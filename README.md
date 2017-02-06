# IPLocator

由redis、Python（uwsgi）、nginx三个组件组成，docker安装略。
以下脚本以代码下载到 /data/dockerdata 目录为例

### 1. 运行redis

    netns_owner=$(docker run -d kubernetes/pause)
    docker run --net=container:${netns_owner} --privileged --rm   busybox sysctl -w net.core.somaxconn=1024
    docker run --net=container:${netns_owner} --privileged --rm   busybox sysctl -w vm.overcommit_memory=1
    docker run --net=container:${netns_owner} --privileged --rm   busybox echo never > /sys/kernel/mm/transparent_hugepage/enabled
    docker run -v /data/data/redis:/data/data/redis -v /data/dockerdata/redis/redis.conf:/usr/local/etc/redis/redis.conf --rm   --net=container:${netns_owner} --name redis_IPLocator  daocloud.io/redis:3.0 redis-server /usr/local/etc/redis/redis.conf &
    
netns_owner相关是用于redis系统参数优化，可忽略。
### 2. 运行Python与初始化

    docker build -t iplocator:1 .
    docker run -it --name iplocator_python --link redis_IPLocator:redisdb --rm iplocator:1 &
    docker exec -it iplocator_python bash /data/server/br13_IPLocator/initipfile.sh 
    
### 2. nginx启动

    docker run -v /data/dockerdata/nginx/nginx.conf:/etc/nginx/nginx.conf:ro --rm -p 9013:9013 --name nginx_iplocator --link iplocator_python:iplocator_container -it nginx &
    
### 3. 宿主机上执行接口，初始化redis

    curl http://127.0.0.1:9013/init
    
### 4. 测试示例

    curl http://127.0.0.1:9013/singleip?ip=123.207.174.172
    netstat -antp|grep tcp|awk '{print $5}'|grep -o '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}' > netstatiplist.txt && curl -F "file=@netstatiplist.txt"   http://127.0.0.1:9013/

上面例子一个是单ip查询，另一个是多ip查询，将生成的netstatiplist.txt文件，上传进行分析。

### 5. 参考文献

    怎么样使用 Redis 来存储和查询 ip 数据
    https://segmentfault.com/a/1190000000352578
    纯真IP库
    https://github.com/gwind/ylinux/tree/master/tools/IP/QQWry
