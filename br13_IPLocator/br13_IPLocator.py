#!/usr/bin/python
# coding=utf-8
from search import *
import time
import os
from flask import Flask, request, redirect, url_for
import uuid
UPLOAD_FOLDER = './tmp'  # 临时文件保存路径
if not os.path.exists('./tmp'):
    os.mkdir('./tmp')
if not os.path.exists('./logs'):
    os.mkdir('./logs')

ipsearcher = ipsearch('doc/ip_clean.world.txt')  # ip数据库文件
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['threadNum'] = 4  # 查询使用的进程数
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
                resultstr = processsearch(str(os.path.join(app.config['UPLOAD_FOLDER'], filename)), newlinestr, app.config['threadNum'])  # 执行查询
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


# @app.route('/uploads/')
# def uploaded_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'],
#                                filename)

def processsearch(ipliststr, newlinestr, processNum=2):  # 重新定义查询，将命令行传参变为函数传参
    # 拷贝自 search.py 基本注释请参考那个文件

    """
    查询ip分布
    :param ipliststr: 待查询ip列表
    :param newlinestr: 换行符 网页应为 <br>
    :param processNum: 使用进程数量
    :return: 返回结果
    """
    # areastr = s.Searchip('223.19.227.103')
    # print(areastr)


    iplist = []
    f = open(ipliststr, buffering=1024*1024)
    for line in f:
        iplist.append(line.strip())


    p = Pool(processes=processNum)
    manager = Manager()
    results_list = []
    for i in range(0, processNum):
        result_dict = manager.dict()
        results_list.append(result_dict)
        p.apply_async(run, [i, ipsearcher, processNum, iplist, result_dict])

    p.close()
    p.join()

    result_dict_all = {}
    for result_dict_l in results_list:
        result_list = result_dict_l.items()   # 开始查询
        for r in result_list:
            result_dict_all[r[0]] = result_dict_all.get(r[0], 0) + result_dict_l.get(r[0], 0)

    taskresultlist = ipsearcher.dicttolist(result_dict_all)
    resultstr = 'result:' + newlinestr
    for c in taskresultlist:
        resultstr = resultstr + ('%s %d%s' % (c[0], c[1], newlinestr) )  # 输出结果

    return resultstr  # 返回结果

if __name__ == '__main__':
    app.run('0.0.0.0', 9090, debug=True)