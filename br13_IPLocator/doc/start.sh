#!/bin/sh
cd /data/server/br13_IPLocator 
uwsgi  -x uwsgi_config.xml  --enable-threads  --thunder-lock

