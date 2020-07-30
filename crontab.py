#coding: utf-8
import public,db,os,web,time,re
class crontab:
    def GetCrontab(self,get):
        self.checkBackup()
        cront = public.M('crontab').order("id desc").field('id,name,type,where1,where_hour,where_minute,echo,addtime').select()
        data=[]
        for i in range(len(cront)):
            tmp=cront[i]
            if cront[i]['type']=="day":
                tmp['type']="Every day"
                tmp['cycle']='Every day, '+str(cront[i]['where_hour'])+' point '+str(cront[i]['where_minute'])+' execution'
            elif cront[i]['type']=="day-n":
                tmp['type']="Each "+str(cront[i]['where1'])+' day'
                tmp['cycle']='Every '+str(cront[i]['where1'])+'day '+str(cront[i]['where_hour'])+' point '+str(cront[i]['where_minute'])+' execution'
            elif cront[i]['type']=="hour":
                tmp['type']="Per hour"
                tmp['cycle']='Per hour, First '+str(cront[i]['where_minute'])+' minute execution'
            elif cront[i]['type']=="hour-n":
                tmp['type']="Each "+str(cront[i]['where1'])+' hour'
                tmp['cycle']='Every '+str(cront[i]['where1'])+' hour '+str(cront[i]['where_minute'])+' minute execution'
            elif cront[i]['type']=="minute-n":
                tmp['type']="Each "+str(cront[i]['where1'])+' minute'
                tmp['cycle']='Every '+str(cront[i]['where1'])+' minute execution'
            elif cront[i]['type']=="week":
                tmp['type']="Weekly"
                tmp['cycle']= 'Weekly '+self.toWeek(int(cront[i]['where1']))+', '+str(cront[i]['where_hour'])+' point '+str(cront[i]['where_minute'])+' execution'
            elif cront[i]['type']=="month":
                tmp['type']="Per month"
                tmp['cycle']='Per month, '+str(cront[i]['where1'])+' day '+str(cront[i]['where_hour'])+' point '+str(cront[i]['where_minute'])+' execution'
            data.append(tmp)
        return data

    def toWeek(self,num):
        wheres={
                0   :   'Sunday',
                1   :   'Monday',
                2   :   'Tuesday',
                3   :   'Wednesday',
                4   :   'Thursday',
                5   :   'Friday',
                6   :   'Saturday'
                }

        try:
            return wheres[num]
        except:
            return ''

    def checkBackup(self):
        if public.ExecShell('/etc/init.d/crond status')[0].find('running') == -1:
            public.ExecShell('/etc/init.d/crond start')

    def AddCrontab(self,get):
        if len(get['name'])<1:
             return public.returnMsg(False,'Task name cannot be empty!')
        cuonConfig=""
        if get['type']=="day":
            cuonConfig = self.GetDay(get)
            name = "Every day"
        elif get['type']=="day-n":
            cuonConfig = self.GetDay_N(get)
            name = "Each "+get['where1']+' day'
        elif get['type']=="hour":
            cuonConfig = self.GetHour(get)
            name = "Per hour"
        elif get['type']=="hour-n":
            cuonConfig = self.GetHour_N(get)
            name = "Per hour"
        elif get['type']=="minute-n":
            cuonConfig = self.Minute_N(get)
        elif get['type']=="week":
            get['where1']=get['week']
            cuonConfig = self.Week(get)
        elif get['type']=="month":
            cuonConfig = self.Month(get)
        cronPath=web.ctx.session.setupPath+'/cron'
        cronName=self.GetShell(get)
        if type(cronName) == dict: return cronName;
        cuonConfig += ' ' + cronPath+'/'+cronName+' >> '+ cronPath+'/'+cronName+'.log 2>&1'
        self.WriteShell(cuonConfig)
        self.CrondReload()
        addData=public.M('crontab').add('name,type,where1,where_hour,where_minute,echo,addtime',(get['name'],get['type'],get['where1'],get['hour'],get['minute'],cronName,time.strftime('%Y-%m-%d %X',time.localtime())))
        if addData>0:
             return public.returnMsg(True,'Added successfully!')
        return public.returnMsg(False,'Add failed!')

    def GetDay(self,param):
        cuonConfig ="{0} {1} * * * ".format(param['minute'],param['hour'])
        return cuonConfig

    def GetDay_N(self,param):
        cuonConfig ="{0} {1} */{2} * * ".format(param['minute'],param['hour'],param['where1'])
        return cuonConfig

    def GetHour(self,param):
        cuonConfig ="{0} * * * * ".format(param['minute'])
        return cuonConfig

    def GetHour_N(self,param):
        cuonConfig ="{0} */{1} * * * ".format(param['minute'],param['where1'])
        return cuonConfig

    def Minute_N(self,param):
        cuonConfig ="*/{0} * * * * ".format(param['where1'])
        return cuonConfig

    def Week(self,param):
        cuonConfig ="{0} {1} * * {2}".format(param['minute'],param['hour'],param['week'])
        return cuonConfig

    def Month(self,param):
        cuonConfig = "{0} {1} {2} * * ".format(param['minute'],param['hour'],param['where1'])
        return cuonConfig

    def GetLogs(self,get):
        id = get['id']
        echo = public.M('crontab').where("id=?",(id,)).field('echo').find()
        logFile = web.ctx.session.setupPath+'/cron/'+echo['echo']+'.log'
        if not os.path.exists(logFile):return public.returnMsg(False, 'The current task log is empty!')
        log = public.readFile(logFile)
        where = "Warning: Using a password on the command line interface can be insecure.\n"
        if  log.find(where)>-1:
            log = log.replace(where, '')
            public.writeFile('/tmp/read.tmp',log)
        return public.returnMsg(True, log)

    def DelLogs(self,get):
        try:
            id = get['id']
            echo = public.M('crontab').where("id=?",(id,)).getField('echo')
            logFile = web.ctx.session.setupPath+'/cron/'+echo+'.log'
            os.remove(logFile)
            return public.returnMsg(True, 'Log has been emptied!')
        except:
            return public.returnMsg(False, 'Failed to clear the log!')

    def DelCrontab(self,get):
        try:
            id = get['id']
            find = public.M('crontab').where("id=?",(id,)).field('name,echo').find()
            file = '/var/spool/cron/root'
            conf=public.readFile(file)
            rep = ".+" + str(find['echo']) + ".+\n"
            conf = re.sub(rep, "", conf)
            cronPath = web.ctx.session.setupPath + '/cron'
            public.writeFile(file,conf)

            sfile = cronPath + '/' + find['echo']
            if os.path.exists(sfile): os.remove(sfile)
            sfile = cronPath + '/' + find['echo'] + '.log'
            if os.path.exists(sfile): os.remove(sfile)

            self.CrondReload()
            public.M('crontab').where("id=?",(id,)).delete()
            public.WriteLog('Scheduled Tasks', 'Delete scheduled task [' + find['name'] + '] success!')
            return public.returnMsg(True, 'Successfully deleted!')
        except:
            return public.returnMsg(False, 'Write configuration to scheduled task failed!')

    def GetShell(self,param):
        try:
            filePath='/tmp/freememory.sh'
            if not os.path.exists(filePath):
                public.downloadFile('https://basoro.id/downloads/freememory.sh',filePath)

            head="#!/bin/bash\nPATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin\nexport PATH\n"
            type=param['sType']
            if type == 'rememory':
                shell = head + '/bin/bash /tmp/freememory.sh';
            elif type == 'toUrl':
                shell = head + 'curl -sS --connect-timeout 10 -m 60 ' + param.urladdress;
            else:
                shell=head+param['sBody']

            shell += '''
echo "----------------------------------------------------------------------------"
endDate=`date +"%Y-%m-%d %H:%M:%S"`
echo "★[$endDate] Task execution succeeded"
echo "----------------------------------------------------------------------------"
'''
            cronPath=web.ctx.session.setupPath+'/cron'
            if not os.path.exists(cronPath): public.ExecShell('mkdir -p ' + cronPath);
            cronName=public.md5(public.md5(str(time.time()) + '_bt'))
            file = cronPath+'/' + cronName
            public.writeFile(file,self.CheckScript(shell))
            public.ExecShell('chmod 750 ' + file)
            return cronName
        except Exception,ex:
            return public.returnMsg(False, 'File write failed!')

    def CheckScript(self,shell):
        keys = ['shutdown','init 0','mkfs','passwd','chpasswd','--stdin','mkfs.ext','mke2fs']
        for key in keys:
            shell = shell.replace(key,'[***]');
        return shell;

    def CrondReload(self):
        if os.path.exists('/usr/bin/systemctl'):
            public.ExecShell("systemctl reload crond")
        else:
            public.ExecShell('/etc/rc.d/init.d/crond reload')

    def WriteShell(self,config):
        file='/var/spool/cron/root'
        if not os.path.exists(file): public.writeFile(file,'')
        conf = public.readFile(file)
        conf += config + "\n"
        if public.writeFile(file,conf):
            public.ExecShell("chmod 600 '" + file + "' && chown root.root " + file)
            return True
        return public.returnMsg(False,'Write configuration to scheduled task failed!')

    def StartTask(self,get):
        echo = public.M('crontab').where('id=?',(get.id,)).getField('echo');
        execstr = web.ctx.session.setupPath + '/cron/' + echo;
        os.system('chmod +x ' + execstr)
        os.system('nohup ' + execstr + ' >> ' + execstr + '.log 2>&1 &');
        return public.returnMsg(True,'Task has been executed!')
