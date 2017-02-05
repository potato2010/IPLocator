#!/usr/bin/python
# coding=utf-8
from redissearch import *
import os
from flask import request, redirect, url_for
import uuid

UPLOAD_FOLDER = './tmp'  # 临时文件保存路径
if not os.path.exists('./tmp'):
    os.mkdir('./tmp')
if not os.path.exists('./logs'):
    os.mkdir('./logs')
from flask import Flask
from flask_redis import FlaskRedis
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# redis
REDIS_URL = "redis://:@redisdb:6379/0"
app.config['REDIS_URL'] = REDIS_URL
redis_store = FlaskRedis(app, strict=False)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if str(request.headers).find('curl') < 0:  # 判断请求客户端不是linux命令 curl
            newlinestr = '<br>'
        else:
            newlinestr = '\r\n'
        if file:
            filename = uuid.uuid4().hex
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # 保存接收到的文件
            try:
                starttime = time.time()
                resultstr = redissearcher(str(os.path.join(app.config['UPLOAD_FOLDER'], filename)), newlinestr)
                # resultstr = processsearch(str(os.path.join(app.config['UPLOAD_FOLDER'], filename)), newlinestr, app.config['threadNum'])  # 执行查询
                stoptime = time.time()
                return '%s\r\nrun time : %d second%s' % (resultstr, (stoptime - starttime), newlinestr)
            except:
                return 'something wrong ,please check iplist file'


    return  '''
            <!doctype html>
            <title>Upload new File</title>
            <h1>Upload new File</h1>
            <form action="" method=post enctype=multipart/form-data>
              <p><input type=file name=file>
                 <input type=submit value=Upload>
            </form>
            '''
@app.route('/singleip', methods=['GET', 'POST'])
def getsingleipArea():
    if request.method == 'GET':
        ip = request.args.get('ip', '')
        ipintlist = []
        ipintlist.append(ipstrtoInt(ip.strip()))
        rawresultlist = searchiplist(ipintlist, redis_store)
        if len(rawresultlist) == 1:
            return rawresultlist[0]
        else:
            return 'error'


@app.route('/init', methods=['GET', 'POST'])
def redisdbinit():
    starttime = time.time()
    r = dbinit(redis_store)
    stoptime = time.time()
    if r :
        resultstr = 'db init finish,run time : %d second' % (stoptime - starttime)
    else:
        resultstr = 'db already init,do nothing'
    return resultstr
# @app.route('/uploads/')
# def uploaded_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'],
#                                filename)

def redissearcher(filepath, newlinestr):


    ipintlist = getipintlistfromFile(filepath)
    rawresultlist = searchiplist(ipintlist, redis_store)
    resultdict = getresultdict(rawresultlist)
    resultlist = dicttolist(resultdict)


    resultstr = 'result:' + newlinestr
    for c in resultlist:
        resultstr = resultstr + ('%s %d%s' % (c[0], c[1], newlinestr) )  # 输出结果

    return resultstr  # 返回结果

if __name__ == '__main__':
    app.run('0.0.0.0', 9090, debug=True)
