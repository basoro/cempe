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
        data['nginx'] = self.StatusNginx()
        data['mysql'] = self.StatusMySQL()
        data['php'] = self.StatusPHP()
        data['phpmyadmin'] = self.PHPMyAdminExt()
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

        execStr = "/etc/init.d/"+get.name+" "+get.type
        statusData = "/opt/slemp/server/panel/data/status-"+get.name+".pl"

        os.system(execStr);
        if get.type != 'reload':
            public.writeFile(statusData,get.type)
        return public.returnMsg(True,'execution succeed');

    def StatusNginx(self):
        import public
        status = public.readFile('/opt/slemp/server/panel/data/status-nginx.pl')
        return status

    def StatusMySQL(self):
        import public
        status = public.readFile('/opt/slemp/server/panel/data/status-mysqld.pl')
        return status

    def StatusPHP(self):
        import public
        status = public.readFile('/opt/slemp/server/panel/data/status-php-fpm.pl')
        return status

    def PHPMyAdminExt(self):
        import public
        extension = public.readFile('/opt/slemp/server/phpmyadmin/default.pl')
        return extension

    def RestartServer(self):
        if not public.IsRestart(): return public.returnMsg(False,'Please wait for all installation tasks to complete before executing!');
        public.ExecShell("/etc/init.d/slemp stop && init 6 &");
        return public.returnMsg(True,'Command sent successfully!');
