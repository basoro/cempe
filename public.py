#coding: utf-8

def M(table):
    import db
    sql = db.Sql()
    return sql.table(table);

def md5(str):
    try:
        import hashlib
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()
    except:
        return False

def GetRandomString(length):
    from random import Random
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    chrlen = len(chars) - 1
    random = Random()
    for i in range(length):
        str+=chars[random.randint(0, chrlen)]
    return str

def returnJson(status,msg):
    return getJson({'status':status,'msg':msg})

def returnMsg(status,msg):
    return {'status':status,'msg':msg}

def getJson(data):
    import json,web
    web.header('Content-Type','application/json; charset=utf-8')
    return json.dumps(data)

def readFile(filename):
    try:
        fp = open(filename, 'r');
        fBody = fp.read()
        fp.close()
        return fBody
    except:
        return False

def getDate():
    import time
    return time.strftime('%Y-%m-%d %X',time.localtime())

def writeFile(filename,str):
    try:
        fp = open(filename, 'w+');
        fp.write(str)
        fp.close()
        return True
    except:
        return False

def httpGet(url):
    try:
        import urllib2
        response = urllib2.urlopen(url)
        return response.read()
    except Exception,ex:
        return str(ex);

def httpPost(url,data):
    try:
        import urllib
        import urllib2
        data = urllib.urlencode(data)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        return response.read()
    except Exception,ex:
        return str(ex);


def ExecShell(cmdstring, cwd=None, timeout=None, shell=True):
    import shlex
    import datetime
    import subprocess
    import time

    if shell:
        cmdstring_list = cmdstring
    else:
        cmdstring_list = shlex.split(cmdstring)
    if timeout:
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=timeout)

    sub = subprocess.Popen(cmdstring_list, cwd=cwd, stdin=subprocess.PIPE,shell=shell,bufsize=4096,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

    while sub.poll() is None:
        time.sleep(0.1)
        if timeout:
            if end_time <= datetime.datetime.now():
                raise Exception("Timeout：%s"%cmdstring)

    return sub.communicate()

def downloadFile(url,filename):
    import urllib
    urllib.urlretrieve(url,filename=filename ,reporthook= downloadHook)

def downloadHook(count, blockSize, totalSize):
    speed = {'total':totalSize,'block':blockSize,'count':count}
    print speed
    print '%02d%%'%(100.0 * count * blockSize / totalSize)


def serviceReload():
    import web
    if web.ctx.session.webserver == 'nginx':
        result = ExecShell('/etc/init.d/nginx reload')
        if result[1].find('nginx.pid') != -1:
            ExecShell('pkill -9 nginx && sleep 1');
            ExecShell('/etc/init.d/nginx start');
    return result;
