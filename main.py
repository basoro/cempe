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
    '/public'  , 'panelPublic',
    '/files'   , 'panelFiles',
    '/download', 'panelDownload',
)


app = web.application(urls, globals())

web.config.session_parameters['cookie_name'] = 'SLEMP_PANEL'
web.config.session_parameters['cookie_domain'] = None
web.config.session_parameters['timeout'] = 3600
web.config.session_parameters['ignore_expiry'] = True
web.config.session_parameters['ignore_change_ip'] = True
web.config.session_parameters['secret_key'] = 'slemp.basoro.id'
web.config.session_parameters['expired_message'] = 'Session expired'
dbfile = '/opt/slemp/server/panel/data/default.db';
sessionDB = web.database(dbn='sqlite', db=dbfile)
session = web.session.Session(app, web.session.DBStore(sessionDB,'sessions'), initializer={'login': False});
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
        password = public.md5(post.password)
        sql = db.Sql()
        userInfo = sql.table('users').where("username=? AND password=?",(post.username,password)).field('id,username,password').find()
        try:
            if userInfo['username'] != post.username or userInfo['password'] != password:
                return public.returnJson(False,'The username or password is incorrect.');

            import time;
            login_temp = 'data/login.temp'
            if not os.path.exists(login_temp): public.writeFile(login_temp,'');
            login_logs = public.readFile(login_temp);
            public.writeFile(login_temp,login_logs+web.ctx.ip+'|'+str(int(time.time()))+',');
            session.login = True
            session.username = post.username
            return public.returnJson(True,'Successful login, jumping!');
        except:
            return public.returnJson(False, 'The username or password is incorrect.');

class panelSystem(common.panelAdmin):
    def GET(self):
        return self.funObj()

    def POST(self):
        return self.funObj()

    def funObj(self):
        import system,json
        get = web.input()
        sysObject = system.system()
        defs = ('GetNetWork','GetDiskInfo','GetCpuInfo','GetBootTime','GetSystemVersion','GetMemInfo','GetSystemTotal','ServiceAdmin','RestartServer','setPassword')
        for key in defs:
            if key == get.action:
                fun = 'sysObject.'+key+'()'
                return public.getJson(eval(fun))
        return public.returnJson(False,'Invalid specified parameter!')

class panelFiles(common.panelAdmin):
    def GET(self):
        return render.files('test')

    def POST(self):
        get = web.input(zunfile = {},data = [])
        if hasattr(get,'path'):
            get.path = get.path.replace('//','/').replace('\\','/');

        import files
        filesObject = files.files()
        defs = ('UploadFile','GetDir','CreateFile','CreateDir','DeleteDir','DeleteFile',
                'CopyFile','CopyDir','MvFile','GetFileBody','SaveFileBody','Zip','UnZip',
                'GetFileAccess','SetFileAccess','GetDirSize','SetBatchData','BatchPaste',
                'DownloadFile')
        for key in defs:
            if key == get.action:
                fun = 'filesObject.'+key+'(get)'
                return public.getJson(eval(fun))

        return public.returnJson(False,'Invalid specified parameter!')

class panelDownload(common.panelAdmin):
    def GET(self):
        get = web.input()
        try:
            get.filename = get.filename.encode('utf-8');
            import os
            fp = open(get.filename,'rb')
            size = os.path.getsize(get.filename)
            filename = os.path.basename(get.filename)

            web.header("Content-Disposition", "attachment; filename=" +filename);
            web.header("Content-Length", size);
            web.header('Content-Type','application/octet-stream')
            buff = 4096
            while True:
                fBody = fp.read(buff)
                if fBody:
                    yield fBody
                else:
                    return
        except Exception, e:
            yield 'Error'
        finally:
            if fp:
                fp.close()

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
