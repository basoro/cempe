#coding: utf-8
import web,os,public
class panelSetup:
    def __init__(self):
        web.ctx.session.webname = 'SLEMP Panel'
        if os.path.exists('data/title.pl'):
            web.ctx.session.webname = public.readFile('data/title.pl');

class panelAdmin(panelSetup):
    def __init__(self):
        web.ctx.session.brand = 'SLEMP Panel'
        web.ctx.session.product = 'Linux'
        web.ctx.session.version = "1.1.3"
        web.ctx.session.rootPath = '/opt/slemp'
        web.ctx.session.webname = 'SLEMP Panel'
        web.ctx.session.downloadUrl = 'https://basoro.id/downloads/slemp';
        web.ctx.session.setupPath = web.ctx.session.rootPath+'/server'
        web.ctx.session.logsPath = web.ctx.session.rootPath+'/wwwlogs'
        setupPath = web.ctx.session.setupPath
        web.ctx.session.webserver = 'nginx'
        filename = setupPath+'/data/phpmyadminDirName.pl'
        web.ctx.session.phpmyadminDir = public.readFile(filename).strip()

        try:
            if not web.ctx.session.login:
                raise web.seeother('/login')
            tmp = web.ctx.host.split(':')
        except:
            raise web.seeother('/login')
        web.ctx.session.server_os = self.GetOS();

    def GetOS(self):
        filename = "/opt/slemp/server/panel/data/osname.pl";
        if not os.path.exists(filename):
            scriptFile = 'script/GetOS.sh'
            if not os.path.exists(scriptFile):
                public.downloadFile('https://basoro.id/downloads/slemp/GetOS.sh',scriptFile);
            os.system("bash /opt/slemp/server/panel/script/GetOS.sh")
        tmp = {}
        tmp['x'] = 'RHEL';
        tmp['osname'] = public.readFile(filename).strip();
        #rs = ['CentOS','RHEL','Fedora']
        #if osname in rs: tmp['x'] = 'RHEL';
        ds = ['Debian','Ubuntu','Raspbian','Deepin']
        if tmp['osname'] in ds: tmp['x'] = 'Debian';
        return tmp
