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

def WriteLog(type,logMsg):
    try:
        import time
        import db
        sql = db.Sql()
        mDate = time.strftime('%Y-%m-%d %X',time.localtime())
        data = (type,logMsg,mDate)
        result = sql.table('logs').add('type,log,addtime',data)
        writeFile('/tmp/test.pl', str(data))
    except:
        pass

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


def serviceReload():
    import web
    if web.ctx.session.webserver == 'nginx':
        result = ExecShell('/etc/init.d/nginx reload')
        if result[1].find('nginx.pid') != -1:
            ExecShell('pkill -9 nginx && sleep 1');
            ExecShell('/etc/init.d/nginx start');
    return result;

def phpReload(version):
    ExecShell('/etc/init.d/php-fpm-'+version+' reload')

def downloadFile(url,filename):
    import urllib
    urllib.urlretrieve(url,filename=filename ,reporthook= downloadHook)

def downloadHook(count, blockSize, totalSize):
    speed = {'total':totalSize,'block':blockSize,'count':count}
    print speed
    print '%02d%%'%(100.0 * count * blockSize / totalSize)


def GetLocalIp():
    try:
        import re;
        filename = 'data/iplist.txt'
        ipaddress = readFile(filename)
        if not ipaddress:
            import urllib2
            url = 'http://pv.sohu.com/cityjson?ie=utf-8'
            opener = urllib2.urlopen(url)
            str = opener.read()
            ipaddress = re.search('\d+.\d+.\d+.\d+',str).group(0)
            writeFile(filename,ipaddress)

        ipaddress = re.search('\d+.\d+.\d+.\d+',ipaddress).group(0);
        return ipaddress
    except:
        try:
            url = 'http://ifconfig.me';
            opener = urllib2.urlopen(url)
            return opener.read()
        except:
            import web
            return web.ctx.host.split(':')[0];

def inArray(arrays,searchStr):
    for key in arrays:
        if key == searchStr: return True

    return False

def checkWebConfig():
    import web
    if web.ctx.session.webserver == 'nginx':
        result = ExecShell(web.ctx.session.setupPath+"/nginx/sbin/nginx -t -c "+web.ctx.session.setupPath+"/nginx/conf/nginx.conf");
        searchStr = 'successful'

    if result[1].find(searchStr) == -1:
        WriteLog("Check configuration", "Configuration file error: "+result[1]);
        return result[1];
    return True;

def checkIp(ip):
    import re
    p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if p.match(ip):
        return True
    else:
        return False

def checkPort(port):
    ports = ['21','25','443','8080','1234','12345','8443'];
    if port in ports: return False;
    intport = int(port);
    if intport < 1 or intport > 65535: return False;
    return True;

def getStrBetween(startStr,endStr,srcStr):
    start = srcStr.find(startStr)
    if start == -1: return None
    end = srcStr.find(endStr)
    if end == -1: return None
    return srcStr[start+1:end]

def getCpuType():
    import re;
    cpuinfo = open('/proc/cpuinfo','r').read();
    rep = "model\s+name\s+:\s+(.+)"
    tmp = re.search(rep,cpuinfo);
    cpuType = None
    if tmp:
        cpuType = tmp.groups()[0];
    return cpuType;

def IsRestart():
    num  = M('tasks').where('status!=?',('1',)).count();
    if num > 0: return False;
    return True;

def hasPwd(password):
    import crypt;
    return crypt.crypt(password,password);

def CheckMyCnf():
    import os;
    confFile = '/etc/my.cnf'
    if not os.path.exists(confFile): return False;
    conf = readFile(confFile)
    if len(conf) > 100: return True;
    versionFile = '/opt/slemp/server/mysql/version.pl';
    if not os.path.exists(versionFile): return False;

    versions = ['5.5','5.6','5.7']
    version = readFile(versionFile);
    for key in versions:
        if key in version:
            version = key;
            break;

    shellStr = '''
#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

Download_Url=https://basoro.id/downloads/slemp

MySQL_Opt()
{
    MemTotal=`free -m | grep Mem | awk '{print  $2}'`
    if [[ ${MemTotal} -gt 1024 && ${MemTotal} -lt 2048 ]]; then
        sed -i "s#^key_buffer_size.*#key_buffer_size = 32M#" /etc/my.cnf
        sed -i "s#^table_open_cache.*#table_open_cache = 128#" /etc/my.cnf
        sed -i "s#^sort_buffer_size.*#sort_buffer_size = 768K#" /etc/my.cnf
        sed -i "s#^read_buffer_size.*#read_buffer_size = 768K#" /etc/my.cnf
        sed -i "s#^myisam_sort_buffer_size.*#myisam_sort_buffer_size = 8M#" /etc/my.cnf
        sed -i "s#^thread_cache_size.*#thread_cache_size = 16#" /etc/my.cnf
        sed -i "s#^query_cache_size.*#query_cache_size = 16M#" /etc/my.cnf
        sed -i "s#^tmp_table_size.*#tmp_table_size = 32M#" /etc/my.cnf
        sed -i "s#^innodb_buffer_pool_size.*#innodb_buffer_pool_size = 128M#" /etc/my.cnf
        sed -i "s#^innodb_log_file_size.*#innodb_log_file_size = 32M#" /etc/my.cnf
    elif [[ ${MemTotal} -ge 2048 && ${MemTotal} -lt 4096 ]]; then
        sed -i "s#^key_buffer_size.*#key_buffer_size = 64M#" /etc/my.cnf
        sed -i "s#^table_open_cache.*#table_open_cache = 256#" /etc/my.cnf
        sed -i "s#^sort_buffer_size.*#sort_buffer_size = 1M#" /etc/my.cnf
        sed -i "s#^read_buffer_size.*#read_buffer_size = 1M#" /etc/my.cnf
        sed -i "s#^myisam_sort_buffer_size.*#myisam_sort_buffer_size = 16M#" /etc/my.cnf
        sed -i "s#^thread_cache_size.*#thread_cache_size = 32#" /etc/my.cnf
        sed -i "s#^query_cache_size.*#query_cache_size = 32M#" /etc/my.cnf
        sed -i "s#^tmp_table_size.*#tmp_table_size = 64M#" /etc/my.cnf
        sed -i "s#^innodb_buffer_pool_size.*#innodb_buffer_pool_size = 256M#" /etc/my.cnf
        sed -i "s#^innodb_log_file_size.*#innodb_log_file_size = 64M#" /etc/my.cnf
    elif [[ ${MemTotal} -ge 4096 && ${MemTotal} -lt 8192 ]]; then
        sed -i "s#^key_buffer_size.*#key_buffer_size = 128M#" /etc/my.cnf
        sed -i "s#^table_open_cache.*#table_open_cache = 512#" /etc/my.cnf
        sed -i "s#^sort_buffer_size.*#sort_buffer_size = 2M#" /etc/my.cnf
        sed -i "s#^read_buffer_size.*#read_buffer_size = 2M#" /etc/my.cnf
        sed -i "s#^myisam_sort_buffer_size.*#myisam_sort_buffer_size = 32M#" /etc/my.cnf
        sed -i "s#^thread_cache_size.*#thread_cache_size = 64#" /etc/my.cnf
        sed -i "s#^query_cache_size.*#query_cache_size = 64M#" /etc/my.cnf
        sed -i "s#^tmp_table_size.*#tmp_table_size = 64M#" /etc/my.cnf
        sed -i "s#^innodb_buffer_pool_size.*#innodb_buffer_pool_size = 512M#" /etc/my.cnf
        sed -i "s#^innodb_log_file_size.*#innodb_log_file_size = 128M#" /etc/my.cnf
    elif [[ ${MemTotal} -ge 8192 && ${MemTotal} -lt 16384 ]]; then
        sed -i "s#^key_buffer_size.*#key_buffer_size = 256M#" /etc/my.cnf
        sed -i "s#^table_open_cache.*#table_open_cache = 1024#" /etc/my.cnf
        sed -i "s#^sort_buffer_size.*#sort_buffer_size = 4M#" /etc/my.cnf
        sed -i "s#^read_buffer_size.*#read_buffer_size = 4M#" /etc/my.cnf
        sed -i "s#^myisam_sort_buffer_size.*#myisam_sort_buffer_size = 64M#" /etc/my.cnf
        sed -i "s#^thread_cache_size.*#thread_cache_size = 128#" /etc/my.cnf
        sed -i "s#^query_cache_size.*#query_cache_size = 128M#" /etc/my.cnf
        sed -i "s#^tmp_table_size.*#tmp_table_size = 128M#" /etc/my.cnf
        sed -i "s#^innodb_buffer_pool_size.*#innodb_buffer_pool_size = 1024M#" /etc/my.cnf
        sed -i "s#^innodb_log_file_size.*#innodb_log_file_size = 256M#" /etc/my.cnf
    elif [[ ${MemTotal} -ge 16384 && ${MemTotal} -lt 32768 ]]; then
        sed -i "s#^key_buffer_size.*#key_buffer_size = 512M#" /etc/my.cnf
        sed -i "s#^table_open_cache.*#table_open_cache = 2048#" /etc/my.cnf
        sed -i "s#^sort_buffer_size.*#sort_buffer_size = 8M#" /etc/my.cnf
        sed -i "s#^read_buffer_size.*#read_buffer_size = 8M#" /etc/my.cnf
        sed -i "s#^myisam_sort_buffer_size.*#myisam_sort_buffer_size = 128M#" /etc/my.cnf
        sed -i "s#^thread_cache_size.*#thread_cache_size = 256#" /etc/my.cnf
        sed -i "s#^query_cache_size.*#query_cache_size = 256M#" /etc/my.cnf
        sed -i "s#^tmp_table_size.*#tmp_table_size = 256M#" /etc/my.cnf
        sed -i "s#^innodb_buffer_pool_size.*#innodb_buffer_pool_size = 2048M#" /etc/my.cnf
        sed -i "s#^innodb_log_file_size.*#innodb_log_file_size = 512M#" /etc/my.cnf
    elif [[ ${MemTotal} -ge 32768 ]]; then
        sed -i "s#^key_buffer_size.*#key_buffer_size = 1024M#" /etc/my.cnf
        sed -i "s#^table_open_cache.*#table_open_cache = 4096#" /etc/my.cnf
        sed -i "s#^sort_buffer_size.*#sort_buffer_size = 16M#" /etc/my.cnf
        sed -i "s#^read_buffer_size.*#read_buffer_size = 16M#" /etc/my.cnf
        sed -i "s#^myisam_sort_buffer_size.*#myisam_sort_buffer_size = 256M#" /etc/my.cnf
        sed -i "s#^thread_cache_size.*#thread_cache_size = 512#" /etc/my.cnf
        sed -i "s#^query_cache_size.*#query_cache_size = 512M#" /etc/my.cnf
        sed -i "s#^tmp_table_size.*#tmp_table_size = 512M#" /etc/my.cnf
        sed -i "s#^innodb_buffer_pool_size.*#innodb_buffer_pool_size = 4096M#" /etc/my.cnf
        sed -i "s#^innodb_log_file_size.*#innodb_log_file_size = 1024M#" /etc/my.cnf
    fi
}

wget -O /etc/my.cnf $Download_Url/install/conf/mysql-%s.conf -T 5
MySQL_Opt
''' % (version,)
    if os.path.exists('data/datadir.pl'):
        newPath = public.readFile('data/datadir.pl');
        mycnf = public.readFile('/etc/my.cnf');
        mycnf = mycnf.replace('/opt/slemp/server/data',newPath);
        public.writeFile('/etc/my.cnf',mycnf);

    os.system(shellStr);
    WriteLog('Daemon', 'MySQL configuration file error detected, may cause the mysqld service to start properly, has been automatically fixed!');
    return True;

def GetNumLines(filename,num):
    fp = open(filename,'r');
    data = []
    l = fp.readline()
    while l:
        data.append(l);
        if len(data) > num: del(data[0]);
        l = fp.readline();
    return "".join(data);

def getPanelAddr():
    import web,os
    protocol = 'https://' if os.path.exists("data/ssl.pl") else 'http://'
    h = web.ctx.host.split(':')
    try:
        result = protocol + h[0] + ':' + h[1]
    except:
        result = protocol + h[0] + ':' + readFile('data/port.pl').strip()
    return result
