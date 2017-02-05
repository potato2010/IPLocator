#!/bin/sh
cd /data/server/br13_IPLocator
uwsgi  --reload logs/uwsgi.pid
