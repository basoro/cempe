#coding: utf-8
import web,os,public
class panelSetup:
    def __init__(self):
        web.ctx.session.webname = 'SLEMP Panel'

class panelAdmin(panelSetup):
    def __init__(self):
        web.ctx.session.brand = 'SLEMP Panel'
        web.ctx.session.product = 'Linux'
        web.ctx.session.version = "1.1.3"
        web.ctx.session.rootPath = '/opt/slemp'
        web.ctx.session.webname = 'SLEMP Panel'
        web.ctx.session.downloadUrl = 'http://basoro.id/downloads/slemp';
        web.ctx.session.setupPath = web.ctx.session.rootPath+'/server'
        web.ctx.session.configPath = web.ctx.session.rootPath+'/wwwroot'
        web.ctx.session.logsPath = web.ctx.session.rootPath+'/wwwlogs'
        setupPath = web.ctx.session.setupPath
        web.ctx.session.webserver = 'nginx'

        try:
            if not web.ctx.session.login:
                raise web.seeother('/login')
            tmp = web.ctx.host.split(':')
        except:
            raise web.seeother('/login')
        web.ctx.session.server_os = self.GetOS();

    def GetOS(self):
        filename = web.ctx.session.setupPath+"/panel/data/osname.pl";
        if not os.path.exists(filename):
            scriptFile = 'GetOS.sh'
            if not os.path.exists(scriptFile):
                public.downloadFile(web.ctx.session.downloadUrl+'/GetOS.sh',scriptFile);
            os.system("bash "+web.ctx.session.setupPath+"/panel/GetOS.sh")
            public.ExecShell("rm -f "+web.ctx.session.setupPath+"/panel/GetOS.sh");
        tmp = {}
        tmp['x'] = 'RHEL';
        tmp['osname'] = public.readFile(filename).strip();
        ds = ['Debian','Ubuntu','Raspbian','Deepin']
        if tmp['osname'] in ds: tmp['x'] = 'Debian';
        return tmp
