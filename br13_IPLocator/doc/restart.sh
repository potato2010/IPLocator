#!/bin/sh
cd /data/server/br13_IPLocator
sh doc/stop.sh
mv logs/uwsgi.log logs/uwsgi.log.`date +%Y_%m_%d`
sh doc/start.sh
