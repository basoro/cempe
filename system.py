#coding: utf-8
import psutil,web,time,os,public,re
class system:
    setupPath = None;

    def __init__(self):
        self.setupPath = web.ctx.session.setupPath;

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

    def ServiceAdmin(self):
        get = web.input()

        if get.name == 'mysqld': public.CheckMyCnf();

        if get.name == 'phpmyadmin':
            import ajax
            get.status = 'True';
            ajax.ajax().setPHPMyAdmin(get);

        elif get.name == 'nginx':
            vhostPath = self.setupPath + '/panel/data/rewrite'
            if not os.path.exists(vhostPath): public.ExecShell('mkdir ' + vhostPath);
            vhostPath = self.setupPath + '/panel/data/vhost'
            if not os.path.exists(vhostPath):
                public.ExecShell('mkdir ' + vhostPath);
                public.ExecShell('/etc/init.d/nginx start');

            result = public.ExecShell('nginx -t -c '+self.setupPath+'/nginx/conf/nginx.conf');
            if result[1].find('perserver') != -1:
                limit = self.setupPath + '/nginx/conf/nginx.conf';
                nginxConf = public.readFile(limit);
                limitConf = "limit_conn_zone $binary_remote_addr zone=perip:10m;\n\t\tlimit_conn_zone $server_name zone=perserver:10m;";
                nginxConf = nginxConf.replace("#limit_conn_zone $binary_remote_addr zone=perip:10m;",limitConf);
                public.writeFile(limit,nginxConf)
                public.ExecShell('/etc/init.d/nginx start');
                return public.returnMsg(True,'Profile mismatch due to reloading Nginx has been fixed!');

            if result[1].find('proxy') != -1:
                import panelSite
                panelSite.panelSite().CheckProxy(get);
                public.ExecShell('/etc/init.d/nginx start');
                return public.returnMsg(True,'Profile mismatch due to reloading Nginx has been fixed!');

            #return result
            if result[1].find('successful') == -1:
                public.WriteLog("Pengaturan ", "Execution failed: "+str(result));
                return public.returnMsg(False,'Nginx configuration rule error: <br><a style="color:red;">'+result[1].replace("\n",'<br>')+'</a>');

        execStr = "/etc/init.d/"+get.name+" "+get.type

        if get.name != 'nginx':
            os.system(execStr);
            return public.returnMsg(True,'execution succeed');
        result = public.ExecShell(execStr)
        if result[1].find('nginx.pid') != -1:
            public.ExecShell('pkill -9 nginx && sleep 1');
            public.ExecShell('/etc/init.d/nginx start');
        if get.type != 'test':
            public.WriteLog("Pengaturan ", execStr+" execution succeed!");
        return public.returnMsg(True,'execution succeed');

    def RestartServer(self):
        if not public.IsRestart(): return public.returnMsg(False,'Please wait for all installation tasks to complete before executing!');
        public.ExecShell("/etc/init.d/slemp stop && init 6 &");
        return public.returnMsg(True,'Command sent successfully!');

    def ReMemory(self):
        scriptFile = 'script/rememory.sh'
        if not os.path.exists(scriptFile):
            public.downloadFile('https://basoro.id/downloads/slemp/rememory.sh',scriptFile);
        public.ExecShell("/bin/bash " + self.setupPath + '/panel/' + scriptFile);
        return self.GetMemInfo();

    def ReWeb(self):
        if not public.IsRestart(): return public.returnMsg(False,'Please wait for all installation tasks to complete before executing!');
        public.ExecShell('/etc/init.d/slemp restart &')
        return True
