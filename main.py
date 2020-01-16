#!/usr/bin/env python
#coding:utf-8
import sys,web,io,os
global panelPath
panelPath = '/opt/slemp/server/panel/';
os.chdir(panelPath)
import common,public,db

from collections import OrderedDict
web.config.debug = False

urls = (
    '/'        , 'panelIndex',
    '/login'   , 'panelLogin',
    '/system'  , 'panelSystem',
    '/public'   , 'panelPublic',
)


app = web.application(urls, globals())

web.config.session_parameters['cookie_name'] = 'SLEMP_PANEL'
web.config.session_parameters['cookie_domain'] = None
web.config.session_parameters['timeout'] = 3600
web.config.session_parameters['ignore_expiry'] = True
web.config.session_parameters['ignore_change_ip'] = True
web.config.session_parameters['secret_key'] = 'slemp.basoro.id'
web.config.session_parameters['expired_message'] = 'Session expired'
dbfile = '/dev/shm/default.db';
src_dbfile = '/opt/slemp/server/panel/data/default.db';
if not os.path.exists('/dev/shm'): os.system('mkdir -p /dev/shm');
if not os.path.exists(dbfile): os.system("\\cp -a -r "+src_dbfile+" " + dbfile);
sessionDB = web.database(dbn='sqlite', db=dbfile)
session = web.session.Session(app, web.session.DBStore(sessionDB,'default'), initializer={'login': False});
def session_hook():
    session.panelPath = os.path.dirname(__file__);
    web.ctx.session = session
app.add_processor(web.loadhook(session_hook))

render = web.template.render(panelPath + 'templates/',base='template',globals={'session': session,'web':web})

class panelIndex(common.panelAdmin):
    def GET(self):
        import system
        data = []
        return render.index(data)

class panelLogin(common.panelSetup):
    def GET(self):
        if not hasattr(session,'webname'): session.webname = 'SLEMP Panel';
        tmp = web.ctx.host.split(':')
        domain = public.readFile('data/domain.conf')
        if domain:
            if(tmp[0].strip() != domain.strip()):
                errorStr = '''
    <meta charset="utf-8">
    <title>Tolak akses</title>
    </head><body>
    <h1>Maaf, Anda tidak memiliki akses</h1>
        <p>Silakan gunakan nama domain yang benar untuk mengakses!</p>
        <p>Lihat nama domain: cat /opt/slemp/server/panel/data/domain.conf</p>
        <p>Matikan limit akses: rm -f /opt/slemp/server/panel/data/domain.conf</p>
    <hr>
    <address>SLEMP Panel 1.x <a href="https://slemp.basoroid" target="_blank">Bantuan</a></address>
    </body></html>
    '''
                web.header('Content-Type','text/html; charset=utf-8', unique=True)
                return errorStr
        if os.path.exists('data/limitip.conf'):
            iplist = public.readFile('data/limitip.conf')
            if iplist:
                if not web.ctx.ip in iplist.split(','):
                    errorStr = '''
<meta charset="utf-8">
<title>Tolak akses</title>
</head><body>
<h1>Maaf, IP Anda tidak diotorisasi</h1>
    <p>IP Anda saat ini adalah [%s], silakan gunakan akses IP yang benar!</p>
    <p>Lihat data IP: cat /opt/slemp/server/panel/data/limitip.conf</p>
    <p>Matikan batasan akses: rm -f /opt/slemp/server/panel/data/limitip.conf</p>
<hr>
<address>SLEMP Panel 1.x <a href="https://slemp.basoroid" target="_blank">Bantuan</a></address>
</body></html>
''' % (web.ctx.ip,)
                    web.header('Content-Type','text/html; charset=utf-8', unique=True)
                    return errorStr;

        get = web.input()
        sql = db.Sql()
        if hasattr(get,'dologin'):
            if session.login != False:
                session.login = False;
                session.kill();
            import time
            time.sleep(0.2);
            raise web.seeother('/login')

        if hasattr(session,'login'):
            if session.login == True:
                raise web.seeother('/')

        data = sql.table('users').getField('username')
        render = web.template.render(panelPath + 'templates/',globals={'session': session})
        return render.login(data)


    def POST(self):
        post = web.input()
        if not (hasattr(post, 'username') or hasattr(post, 'password')):
            return public.returnJson(False,'Nama pengguna atau kata sandi tidak boleh kosong');

        if self.limitAddress('?') < 1: return public.returnJson(False,'Anda gagal masuk berkali-kali, silahkan coba beberapa saat lagi!');
        password = public.md5(post.password)

        sql = db.Sql()
        userInfo = sql.table('users').where("username=? AND password=?",(post.username,password)).field('id,username,password').find()
        try:
            if userInfo['username'] != post.username or userInfo['password'] != password:
                public.WriteLog('Landing',' <a style="color:red;">Wrong password</a>, username: '+post.username+', password: '+post.password+', login IP: '+ web.ctx.ip);
                num = self.limitAddress('+');
                return public.returnJson(False,'The username or password is incorrect, you can also try ['+str(num)+'] times.');

            import time;
            login_temp = 'data/login.temp'
            if not os.path.exists(login_temp): public.writeFile(login_temp,'');
            login_logs = public.readFile(login_temp);
            public.writeFile(login_temp,login_logs+web.ctx.ip+'|'+str(int(time.time()))+',');
            session.login = True
            session.username = post.username
            public.WriteLog('Login', '<a style="color:#3498DB;">Login successfully</a>, username: '+post.username+', login IP: '+ web.ctx.ip);
            self.limitAddress('-');
            return public.returnJson(True,'Successful login, jumping!');
        except:
            public.WriteLog('Login', '<a style="color:red;">Password error</a>, username: '+post.username+', password: '+post.password+', login IP: '+ web.ctx.ip);
            num = self.limitAddress('+');
            return public.returnJson(False, 'The username or password is incorrect, you can also try ['+str(num)+'] times.');

    def limitAddress(self,type):
        import time
        logFile = 'data/'+web.ctx.ip+'.login';
        timeFile = 'data/'+web.ctx.ip+'_time.login';
        limit = 6;
        outtime = 1800;
        try:

            if not os.path.exists(timeFile): public.writeFile(timeFile,str(time.time()));
            if not os.path.exists(logFile): public.writeFile(logFile,'0');

            time1 = long(public.readFile(timeFile).split('.')[0]);
            if (time.time() - time1) > outtime:
                public.writeFile(logFile,'0');
                public.writeFile(timeFile,str(time.time()));

            num1 = int(public.readFile(logFile));
            if type == '+':
                num1 += 1;
                public.writeFile(logFile,str(num1));

            if type == '-':
                public.ExecShell('rm -f data/*.login');
                return 1;

            return limit - num1;
        except:
            return limit;


class panelSystem(common.panelAdmin):
    def GET(self):
        return self.funObj()

    def POST(self):
        return self.funObj()

    def funObj(self):
        import system,json
        get = web.input()
        sysObject = system.system()
        defs = ('GetNetWork','GetDiskInfo','GetCpuInfo','GetBootTime','GetSystemVersion','GetMemInfo','GetSystemTotal','RestartServer')
        for key in defs:
            if key == get.action:
                fun = 'sysObject.'+key+'()'
                return public.getJson(eval(fun))
        return public.returnJson(False,'Invalid specified parameter!')

def publicObject(toObject,defs):
    get = web.input();
    for key in defs:
        if key == get.action:
            fun = 'toObject.'+key+'(get)'
            return public.getJson(eval(fun))

    return public.returnJson(False,'Invalid specified parameter!')

def notfound():
    errorStr = '''
    <meta charset="utf-8">
    <title>404 Not Found</title>
    </head><body>
    <h1>Maaf, halaman tidak ada.</h1>
        <p>Halaman yang Anda minta tidak ada. Harap periksa apakah alamat URL benar.!</p>
    <hr>
    <address>SLEMP Panel 1.x <a href="https://slemp.basoro.id" target="_blank">Bantuan</a></address>
    </body></html>
    '''
    return web.notfound(errorStr);

def internalerror():
    errorStr = '''
    <meta charset="utf-8">
    <title>500 Internal Server Error</title>
    </head><body>
    <h1>Maaf, cilukba....!!</h1>
        <p>Halaman yang anda minta rusak!</p>
    <hr>
    <address>SLEMP Panel 1.x <a href="https://slemp.basoro.id" target="_blank">Bantuan</a></address>
    </body></html>
    '''
    return web.internalerror(errorStr)

if __name__ == "__main__":
    app.notfound = notfound
    app.internalerror = internalerror
    reload(sys)
    sys.setdefaultencoding("utf-8")
    app.run()
