FROM centos:7
MAINTAINER potatoonair <wuzhi2010@gmail.com>
COPY requirements.txt requirements.txt
RUN  yum install wget python-setuptools gcc python-devel libxml2-devel -y \
&& easy_install -i http://pypi.douban.com/simple/ pip \
&& pip install -i http://pypi.douban.com/simple/  --trusted-host  pypi.douban.com  -r requirements.txt \
&& yum clean all
#WORKDIR /data/server
COPY br13_IPLocator /data/server/br13_IPLocator
ENTRYPOINT ["/data/server/br13_IPLocator/startup.sh"]
EXPOSE 9013

