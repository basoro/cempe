#coding: utf-8
import psutil,web,time,os,public,re
class system:
    setupPath = None;

    def __init__(self):
        self.setupPath = web.ctx.session.setupPath;

    def GetConcifInfo(self):
        if not hasattr(web.ctx.session, 'config'):
            web.ctx.session.config = public.M('config').where("id=?",('1',)).field('webserver,sites_path,backup_path,status,mysql_root').find();
        if not hasattr(web.ctx.session.config,'email'):
            web.ctx.session.config['email'] = public.M('users').where("id=?",('1',)).getField('email');
        data = {}
        data = web.ctx.session.config
        data['webserver'] = web.ctx.session.config['webserver']
        phpVersions = ('56','70','71','72','73')

        data['php'] = []

        for version in phpVersions:
            tmp = {}
            tmp['setup'] = os.path.exists(self.setupPath + '/php/'+version+'/bin/php');
            if tmp['setup']:
                phpConfig = self.GetPHPConfig(version)
                tmp['version'] = version
                tmp['max'] = phpConfig['max']
                tmp['maxTime'] = phpConfig['maxTime']
                tmp['pathinfo'] = phpConfig['pathinfo']
                tmp['status'] = os.path.exists('/tmp/php-cgi-'+version+'.sock')
                data['php'].append(tmp)

        tmp = {}
        data['webserver'] = ''
        serviceName = 'nginx'
        tmp['setup'] = False
        phpversion = "56"
        phpport = '1234';
        pstatus = False;
        pauth = False;
        if os.path.exists(self.setupPath+'/nginx'):
            data['webserver'] = 'nginx'
            serviceName = 'nginx'
            tmp['setup'] = os.path.exists(self.setupPath +'/nginx/sbin/nginx');
            configFile = self.setupPath + '/nginx/conf/nginx.conf';
            try:
                if os.path.exists(configFile):
                    conf = public.readFile(configFile);
                    rep = "listen\s+([0-9]+)\s*;";
                    rtmp = re.search(rep,conf);
                    if rtmp:
                        phpport = rtmp.groups()[0];

                    if conf.find('AUTH_START') != -1: pauth = True;
                    if conf.find(self.setupPath + '/stop') == -1: pstatus = True;
                    configFile = self.setupPath + '/nginx/conf/enable-php.conf';
                    conf = public.readFile(configFile);
                    rep = "php-cgi-([0-9]+)\.sock";
                    rtmp = re.search(rep,conf);
                    if rtmp:
                        phpversion = rtmp.groups()[0];
            except:
                pass;

        tmp['type'] = data['webserver']
        tmp['version'] = public.readFile(self.setupPath + '/'+data['webserver']+'/version.pl')
        tmp['status'] = False
        result = public.ExecShell('/etc/init.d/' + serviceName + ' status')
        if result[0].find('running') != -1: tmp['status'] = True
        data['web'] = tmp

        tmp = {}
        vfile = self.setupPath + '/phpmyadmin/version.pl';
        tmp['version'] = public.readFile(vfile);
        tmp['setup'] = os.path.exists(vfile);
        tmp['status'] = pstatus;
        tmp['phpversion'] = phpversion;
        tmp['port'] = phpport;
        tmp['auth'] = pauth;
        data['phpmyadmin'] = tmp;

        tmp = {}
        tmp['setup'] = os.path.exists(self.setupPath +'/mysql/bin/mysql');
        tmp['version'] = public.readFile(self.setupPath + '/mysql/version.pl')
        tmp['status'] = os.path.exists('/tmp/mysql.sock')
        data['mysql'] = tmp

        data['systemdate'] = public.ExecShell('date +"%Y-%m-%d %H:%M:%S %Z %z"')[0];


        return data

    def GetPHPConfig(self,version):
        file = self.setupPath + "/php/"+version+"/etc/php.ini"
        phpini = public.readFile(file)
        file = self.setupPath + "/php/"+version+"/etc/php-fpm.conf"
        phpfpm = public.readFile(file)
        data = {}
        try:
            rep = "upload_max_filesize\s*=\s*([0-9]+)M"
            tmp = re.search(rep,phpini).groups()
            data['max'] = tmp[0]
        except:
            data['max'] = '50'
        try:
            rep = "request_terminate_timeout\s*=\s*([0-9]+)\n"
            tmp = re.search(rep,phpfpm).groups()
            data['maxTime'] = tmp[0]
        except:
            data['maxTime'] = 0

        try:
            rep = ur"\n;*\s*cgi\.fix_pathinfo\s*=\s*([0-9]+)\s*\n"
            tmp = re.search(rep,phpini).groups()

            if tmp[0] == '1':
                data['pathinfo'] = True
            else:
                data['pathinfo'] = False
        except:
            data['pathinfo'] = False

        return data


    def GetSystemTotal(self):
        data = self.GetMemInfo()
        cpu = self.GetCpuInfo()
        data['cpuNum'] = cpu[1]
        data['cpuRealUsed'] = cpu[0]
        data['time'] = self.GetBootTime()
        data['system'] = self.GetSystemVersion()
        return data

    def GetSystemVersion(self):
        import public
        version = public.readFile('/etc/redhat-release')
        if not version:
            version = public.readFile('/etc/issue').replace('\\n \\l','').strip();
        else:
            version = version.replace('release ','').strip();
        return version

    def GetBootTime(self):
        import public,math
        conf = public.readFile('/proc/uptime').split()
        tStr = float(conf[0])
        min = tStr / 60;
        hours = min / 60;
        days = math.floor(hours / 24);
        hours = math.floor(hours - (days * 24));
        min = math.floor(min - (days * 60 * 24) - (hours * 60));
        data = ""
        data = str(int(days))+" Hari "
        data += str(int(hours))+" Jam "
        data += str(int(min))+" Menit"
        return (data,)

    def GetCpuInfo(self):
        cpuCount = psutil.cpu_count()
        used = psutil.cpu_percent(interval=1)
        return used,cpuCount

    def GetMemInfo(self):
        mem = psutil.virtual_memory()
        memInfo = {'memTotal':mem.total/1024/1024,'memFree':mem.free/1024/1024,'memBuffers':mem.buffers/1024/1024,'memCached':mem.cached/1024/1024}
        memInfo['memRealUsed'] = memInfo['memTotal'] - memInfo['memFree'] - memInfo['memBuffers'] - memInfo['memCached']
        return memInfo

    def GetDiskInfo(self):
        return self.GetDiskInfo2();
        diskIo = psutil.disk_partitions()
        diskInfo = []

        for disk in diskIo:
            if disk[1] == '/mnt/cdrom':continue;
            if disk[1] == '/boot':continue;
            tmp = {}
            tmp['path'] = disk[1]
            tmp['size'] = psutil.disk_usage(disk[1])
            diskInfo.append(tmp)
        return diskInfo

    def GetDiskInfo2(self):
        temp = public.ExecShell("df -h -P|grep '/'|grep -v tmpfs")[0];
        temp1 = temp.split('\n');
        diskInfo = [];
        cuts = ['/mnt/cdrom','/boot','boot/efi','/dev','/dev/shm'];
        for tmp in temp1:
            disk = tmp.split();
            if len(disk) < 5: continue;
            if len(disk[5]) > 24: continue;
            if disk[5] in cuts: continue;
            arr = {}
            arr['path'] = disk[5];
            tmp1 = [disk[1],disk[2],disk[3],disk[4]];
            arr['size'] = tmp1;
            diskInfo.append(arr);
        return diskInfo

    def GetNetWork(self):
        networkIo = psutil.net_io_counters()[:4]
        if not hasattr(web.ctx.session,'up'):
            web.ctx.session.up   =  networkIo[0]
            web.ctx.session.down =  networkIo[1]
        networkInfo = {}
        networkInfo['upTotal']   = networkIo[0]
        networkInfo['downTotal'] = networkIo[1]
        networkInfo['up']        = round(float(networkIo[0] - web.ctx.session.up) / 1024 / 3,2)
        networkInfo['down']      = round(float(networkIo[1] - web.ctx.session.down) / 1024 / 3,2)
        networkInfo['downPackets'] =networkIo[3]
        networkInfo['upPackets']   =networkIo[2]

        web.ctx.session.up   =  networkIo[0]
        web.ctx.session.down =  networkIo[1]

        networkInfo['cpu'] = self.GetCpuInfo()
        return networkInfo

    def RestartServer(self):
        if not public.IsRestart(): return public.returnMsg(False,'Please wait for all installation tasks to complete before executing!');
        public.ExecShell("/etc/init.d/slemp stop && init 6 &");
        return public.returnMsg(True,'Command sent successfully!');
