 #coding: utf-8
import public,os,web
class ajax:

    def GetNginxStatus(self,get):
        self.CheckStatusConf();
        result = public.httpGet('http://127.0.0.1/nginx_status')
        tmp = result.split()
        data = {}
        data['active']   = tmp[2]
        data['accepts']  = tmp[9]
        data['handled']  = tmp[7]
        data['requests'] = tmp[8]
        data['Reading']  = tmp[11]
        data['Writing']  = tmp[13]
        data['Waiting']  = tmp[15]
        return data

    def GetPHPStatus(self,get):
        self.CheckStatusConf();
        import json,time,web
        version = web.input(version='56').version
        result = public.httpGet('http://127.0.0.1/phpfpm_'+version+'_status?json')
        tmp = json.loads(result)
        fTime = time.localtime(int(tmp['start time']))
        tmp['start time'] = time.strftime('%Y-%m-%d %H:%M:%S',fTime)
        return tmp

    def CheckStatusConf(self):
        if web.ctx.session.webserver != 'nginx': return;
        filename = web.ctx.session.setupPath + '/panel/data/vhost/phpfpm_status.conf';
        if os.path.exists(filename): return;

        conf = '''server {
    listen 80;
    server_name 127.0.0.1;
    allow 127.0.0.1;
    location /nginx_status {
        stub_status on;
        access_log off;
    }
    location /phpfpm_56_status {
        fastcgi_pass unix:/tmp/php-cgi-56.sock;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME \$fastcgi_script_name;
    }
    location /phpfpm_70_status {
        fastcgi_pass unix:/tmp/php-cgi-70.sock;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME \$fastcgi_script_name;
    }
    location /phpfpm_71_status {
        fastcgi_pass unix:/tmp/php-cgi-71.sock;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME \$fastcgi_script_name;
    }
    location /phpfpm_72_status {
        fastcgi_pass unix:/tmp/php-cgi-72.sock;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME \$fastcgi_script_name;
    }
    location /phpfpm_73_status {
        fastcgi_pass unix:/tmp/php-cgi-73.sock;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME \$fastcgi_script_name;
    }
}'''
        public.writeFile(filename,conf);
        public.serviceReload();


    def GetTaskCount(self,get):
        return public.M('tasks').where("status!=?",('1',)).count()

    def GetNetWorkList(self,get):
        import psutil
        netstats = psutil.net_connections()
        networkList = []
        for netstat in netstats:
            tmp = {}
            if netstat.type == 1:
                tmp['type'] = 'tcp'
            else:
                tmp['type'] = 'udp'
            tmp['family']   = netstat.family
            tmp['laddr']    = netstat.laddr
            tmp['raddr']    = netstat.raddr
            tmp['status']   = netstat.status
            p = psutil.Process(netstat.pid)
            tmp['process']  = p.name()
            tmp['pid']      = netstat.pid
            networkList.append(tmp)
            del(p)
            del(tmp)
        networkList = sorted(networkList, key=lambda x : x['status'], reverse=True);
        return networkList;

    def GetProcessList(self,get):
        import psutil,pwd
        Pids = psutil.pids();

        processList = []
        for pid in Pids:
            try:
                tmp = {}
                p = psutil.Process(pid);
                if p.exe() == "": continue;

                tmp['name'] = p.name();
                if self.GoToProcess(tmp['name']): continue;

                tmp['pid'] = pid;
                tmp['status'] = p.status();
                tmp['user'] = p.username();
                cputimes = p.cpu_times()
                if cputimes.user > 1:
                    tmp['cpu_percent'] = p.cpu_percent(interval = 0.5);
                else:
                    tmp['cpu_percent'] = 0.0
                tmp['cpu_times'] = cputimes.user
                tmp['memory_percent'] = round(p.memory_percent(),3)
                pio = p.io_counters()
                tmp['io_write_bytes'] = pio.write_bytes
                tmp['io_read_bytes'] = pio.read_bytes
                tmp['threads'] = p.num_threads()

                processList.append(tmp);
                del(p)
                del(tmp)
            except:
                continue;
        import operator
        processList = sorted(processList, key=lambda x : x['memory_percent'], reverse=True);
        processList = sorted(processList, key=lambda x : x['cpu_times'], reverse=True);
        return processList

    def KillProcess(self,get):
        import psutil
        p = psutil.Process(int(get.pid));
        name = p.name();
        if name == 'python': return public.returnMsg(False,'Gagal mematikan proses ini!');

        p.kill();
        public.WriteLog('Manajemen proses',' Sukses mematikan ['+name+'] dengan ['+get.pid+']!');
        return public.returnMsg(True,'Proses ['+name+'] dengan ['+get.pid+'] telah mati!');

    def GoToProcess(self,name):
        ps = ['sftp-server','login','nm-dispatcher','irqbalance','qmgr','wpa_supplicant','lvmetad','auditd','master','dbus-daemon','tapdisk','sshd','init','ksoftirqd','kworker','kmpathd','kmpath_handlerd','python','kdmflush','bioset','crond','kthreadd','migration','rcu_sched','kjournald','iptables','systemd','network','dhclient','systemd-journald','NetworkManager','systemd-logind','systemd-udevd','polkitd','tuned','rsyslogd']

        for key in ps:
            if key == name: return True

        return False


    def GetNetWorkIo(self,get):
        data =  public.M('network').dbfile('system').where("addtime>=? AND addtime<=?",(get.start,get.end)).field('id,up,down,total_up,total_down,down_packets,up_packets,addtime').order('id asc').select()
        return self.ToAddtime(data);

    def GetDiskIo(self,get):
        data = public.M('diskio').dbfile('system').where("addtime>=? AND addtime<=?",(get.start,get.end)).field('id,read_count,write_count,read_bytes,write_bytes,read_time,write_time,addtime').order('id asc').select()
        return self.ToAddtime(data);
    def GetCpuIo(self,get):
        data = public.M('cpuio').dbfile('system').where("addtime>=? AND addtime<=?",(get.start,get.end)).field('id,pro,mem,addtime').order('id asc').select()
        return self.ToAddtime(data,True);


    def ToAddtime(self,data,tomem = False):
        import time

        if tomem:
            import psutil
            mPre = (psutil.virtual_memory().total / 1024 / 1024) / 100
        length = len(data);
        he = 1;
        if length > 100: he = 2;
        if length > 1000: he = 8;
        if length > 10000: he = 20;
        if he == 1:
            for i in range(length):
                data[i]['addtime'] = time.strftime('%m/%d %H:%M',time.localtime(float(data[i]['addtime'])))
                if tomem and data[i]['mem'] > 100: data[i]['mem'] = data[i]['mem'] / mPre

            return data
        else:
            count = 0;
            tmp = []
            for value in data:
                if count < he:
                    count += 1;
                    continue;
                value['addtime'] = time.strftime('%m/%d %H:%M',time.localtime(float(value['addtime'])))
                if tomem and value['mem'] > 100: value['mem'] = value['mem'] / mPre
                tmp.append(value);
                count = 0;
            return tmp;

    def GetInstalleds(self,softlist):
        softs = '';
        for soft in softlist:
            try:
                for v in soft['versions']:
                    if v['status']: softs += soft['name'] + '-' + v['version'] + '|';
            except:
                continue;

        return softs;

    def CheckInstalled(self,get):
        checks = ['nginx','php','mysql'];
        import os,web
        for name in checks:
            filename = web.ctx.session.rootPath + "/server/" + name
            if os.path.exists(filename): return True;
        return False;

    def GetInstalled(self,get):
        import system
        data = system.system().GetConcifInfo()
        return data;

    def GetPHPConfig(self,get):
        import web,re,json
        filename = web.ctx.session.setupPath + '/php/' + get.version + '/etc/php.ini'
        if not os.path.exists(filename): return public.returnMsg(False,'Versi PHP yang dipilih tidak ada!');
        phpini = public.readFile(filename);
        data = {}
        rep = "disable_functions\s*=\s*(.+)\n"
        tmp = re.search(rep,phpini).groups();
        data['disable_functions'] = tmp[0];

        rep = "upload_max_filesize\s*=\s*([0-9]+)M"
        tmp = re.search(rep,phpini).groups()
        data['max'] = tmp[0]

        rep = ur"\n;*\s*cgi\.fix_pathinfo\s*=\s*([0-9]+)\s*\n"
        tmp = re.search(rep,phpini).groups()
        if tmp[0] == '0':
            data['pathinfo'] = False
        else:
            data['pathinfo'] = True

        phplib = json.loads(public.readFile('data/phplib.conf'));
        libs = [];
        tasks = public.M('tasks').where("status!=?",('1',)).field('status,name').select()
        for lib in phplib:
            lib['task'] = '1';
            for task in tasks:
                tmp = public.getStrBetween('[',']',task['name'])
                if not tmp:continue;
                tmp1 = tmp.split('-');
                if tmp1[0].lower() == lib['name'].lower():
                    lib['task'] = task['status'];
                    lib['phpversions'] = []
                    lib['phpversions'].append(tmp1[1])
            if phpini.find(lib['check']) == -1:
                lib['status'] = False
            else:
                lib['status'] = True

            libs.append(lib)

        data['libs'] = libs;
        return data

    def GetPHPInfo(self,get):
        self.CheckPHPINFO();
        sPath = web.ctx.session.setupPath + '/phpinfo/' + get.version;
        if not os.path.exists(sPath + '/phpinfo.php'):
            public.ExecShell("mkdir -p " + sPath);
            public.writeFile(sPath + '/phpinfo.php','<?php phpinfo(); ?>');
        phpinfo = public.httpGet('http://127.0.0.2/' + get.version + '/phpinfo.php');
        return phpinfo;

    def CheckPHPINFO(self):
        php_versions = ['56','70','71','72','73'];
        path = web.ctx.session.setupPath + '/panel/data/vhost/phpinfo.conf';
        if not os.path.exists(path):
            opt = "";
            for version in php_versions:
                opt += "\n\tlocation /"+version+" {\n\t\tinclude enable-php-"+version+".conf;\n\t}";

            phpinfoBody = '''server
{
    listen 80;
    server_name 127.0.0.2;
    allow 127.0.0.1;
    index phpinfo.php index.html index.php;
    root  /opt/slemp/server/phpinfo;
%s
}''' % (opt,);
            public.writeFile(path,phpinfoBody);

        public.serviceReload();

    def delClose(self,get):
        public.M('logs').where('id>?',(0,)).delete();
        public.WriteLog('Pengaturan panel','Log panel telah dikosongkan!');
        return public.returnMsg(True,'Dibersihkan!');

    def setPHPMyAdmin(self,get):
        import re;
        if web.ctx.session.webserver == 'nginx':
            filename = web.ctx.session.setupPath + '/nginx/conf/nginx.conf';

        conf = public.readFile(filename);
        if hasattr(get,'port'):
            mainPort = public.readFile('data/port.pl').strip();
            if mainPort == get.port:
                return public.returnMsg(False,'Tidak dapat diatur ke port yang sama dengan panel!');
            if web.ctx.session.webserver == 'nginx':
                rep = "listen\s+([0-9]+)\s*;"
                oldPort = re.search(rep,conf).groups()[0];
                conf = re.sub(rep,'listen ' + get.port + ';\n',conf);
            else:
                rep = "Listen\s+([0-9]+)\s*\n";
                oldPort = re.search(rep,conf).groups()[0];
                conf = re.sub(rep,"Listen " + get.port + "\n",conf,1);
                rep = "VirtualHost\s+\*:[0-9]+"
                conf = re.sub(rep,"VirtualHost *:" + get.port,conf,1);


            public.writeFile(filename,conf);
            import firewalls
            get.ps = 'Port phpMyAdmin baru';
            fw = firewalls.firewalls();
            fw.AddAcceptPort(get);
            public.serviceReload();
            public.WriteLog('Manajemen perangkat lunak','Ubah port runtime phpMyAdmin menjadi '+get.port+'!')
            get.id = public.M('firewall').where('port=?',(oldPort,)).getField('id');
            get.port = oldPort;
            fw.DelAcceptPort(get);
            return public.returnMsg(True,'Port berhasil dimodifikasi.!');

        if hasattr(get,'phpversion'):
            if web.ctx.session.webserver == 'nginx':
                filename = web.ctx.session.setupPath + '/nginx/conf/enable-php.conf';
                conf = public.readFile(filename);
                rep = "php-cgi.*\.sock"
                conf = re.sub(rep,'php-cgi-' + get.phpversion + '.sock',conf);
            else:
                rep = "php-cgi.*\.sock"
                conf = re.sub(rep,'php-cgi-' + get.phpversion + '.sock',conf);

            public.writeFile(filename,conf);
            public.serviceReload();
            public.WriteLog('Manajemen perangkat lunak','Ubah phpMyAdmin untuk menjalankan versi PHP '+get.phpversion+'!')
            return public.returnMsg(True,'Versi PHP berhasil dimodifikasi!');

        if hasattr(get,'password'):
            import panelSite;
            if(get.password == 'close'):
                return panelSite.panelSite().CloseHasPwd(get);
            else:
                return panelSite.panelSite().SetHasPwd(get);

        if hasattr(get,'status'):
            if conf.find(web.ctx.session.setupPath + '/stop') != -1:
                conf = conf.replace(web.ctx.session.setupPath + '/stop',web.ctx.session.setupPath + '/phpmyadmin');
                msg = 'Aktifkan'
            else:
                conf = conf.replace(web.ctx.session.setupPath + '/phpmyadmin',web.ctx.session.setupPath + '/stop');
                msg = 'Nonaktifkan'

            public.writeFile(filename,conf);
            public.serviceReload();
            public.WriteLog('Manajemen perangkat lunak','phpMyAdmin punya '+msg+'!')
            return public.returnMsg(True,'phpMyAdmin punya '+msg+'!');

    def ToPunycode(self,get):
        import re;
        get.domain = get.domain.encode('utf8');
        tmp = get.domain.split('.');
        newdomain = '';
        for dkey in tmp:
                match = re.search(u"[\x80-\xff]+",dkey);
                if not match:
                        newdomain += dkey + '.';
                else:
                        newdomain += 'xn--' + dkey.decode('utf-8').encode('punycode') + '.'

        return newdomain[0:-1];

    def phpSort(self,get):
        if public.writeFile('/opt/slemp/server/php/sort.pl',get.ssort): return public.returnMsg(True,'Simpan sortir dengan sukses!');
        return public.returnMsg(False,'Gagal menyimpan!');
