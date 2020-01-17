#!/usr/bin/env python
#coding:utf-8
import sys,os,public,time
reload(sys)
sys.setdefaultencoding('utf-8')
class files:
    def CheckDir(self,path):
        import web
        if path[-1:] == '/':
            path = path[:-1]

        nDirs = ('/',
                '/*',
                '/root',
                '/boot',
                '/bin',
                '/etc',
                '/home',
                '/dev',
                '/sbin',
                '/var',
                '/usr',
                '/tmp',
                '/sys',
                '/proc',
                '/media',
                '/mnt',
                '/opt',
                '/lib',
                '/srv',
                '/selinux',
                '/opt/slemp/server',
                web.ctx.session.rootPath,
                web.ctx.session.logsPath,
                web.ctx.session.setupPath)
        for dir in nDirs:
            if(dir == path):
                return False
        return True

    def UploadFile(self,get):
        get.path = get.path.encode('utf-8');
        if get.path.find(':\\') != -1:
            tmp = get.path.split('\\');
            get.path = tmp[len(tmp)-1];
        try:
            if not os.path.exists(get.path): os.makedirs(get.path);
            filename = (get['path'] + get['zunfile'].filename).encode('utf-8');
            fp = open(filename,'w+');
            fp.write(get['zunfile'].file.read());
            fp.close()
            os.system('chown www.www ' + filename);
            public.WriteLog('Document management','Upload files ['+get['zunfile'].filename+'] to ['+get['path']+'] success!')
            return public.returnMsg(True,'Upload success')
        except:
            import time
            opt = time.strftime('%Y-%m-%d_%H%M%S',time.localtime())
            tmp = get['zunfile'].filename.split('.');
            if len(tmp) < 2:
                ext = ""
            else:
                ext = "." + tmp[-1];
            filename = get['path'] + "New_uploaded_files_" + opt + ext;
            fp = open(filename.encode('utf-8'),'w+');
            fp.write(get['zunfile'].file.read());
            fp.close()
            os.system('chown www.www ' + filename);
            public.WriteLog('Document management','Upload files ['+"New_uploaded_files_" + opt + ext+'] to ['+get['path']+'] success!')
            return public.returnMsg(True,'Upload success')

    def GetDir(self,get):
        get.path = get.path.encode('utf-8');
        #if get.path.find('/opt/slemp/wwwroot') == -1: get.path = '/opt/slemp/wwwroot';
        if not os.path.exists(get.path): get.path = '/opt/slemp'

        import pwd
        dirnames = []
        filenames = []
        for filename in os.listdir(get.path):
            try:
                filePath = (get.path+'/'+filename).encode('utf8')
                if os.path.islink(filePath): continue
                stat = os.stat(filePath)
                accept = str(oct(stat.st_mode)[-3:])
                mtime = str(int(stat.st_mtime))
                user = ''
                try:
                    user = pwd.getpwuid(stat.st_uid).pw_name
                except:
                    user = str(stat.st_uid)
                size = str(stat.st_size)
                if os.path.isdir(filePath):
                    dirnames.append(filename+';'+size+';'+mtime+';'+accept+';'+user)
                else:
                    filenames.append(filename+';'+size+';'+mtime+';'+accept+';'+user)
            except:
                continue;

        data = {}
        data['DIR'] = sorted(dirnames);
        data['FILES'] = sorted(filenames);
        data['PATH'] = get.path
        if hasattr(get,'disk'):
            import system
            data['DISK'] = system.system().GetDiskInfo();
        return data

    def CreateFile(self,get):
        get.path = get.path.encode('utf-8');
        try:
            if os.path.exists(get.path):
                return public.returnMsg(False,'The specified file already exists!')

            path = os.path.dirname(get.path)
            if not os.path.exists(path):
                os.makedirs(path)
            open(get.path,'w+').close()
            self.SetFileAccept(get.path);
            public.WriteLog('Document management','Create a file ['+get.path+'] success!')
            return public.returnMsg(True,'The file was created successfully!')
        except:
            return public.returnMsg(False,'File creation failed!')

    def CreateDir(self,get):
        get.path = get.path.encode('utf-8');
        try:
            if os.path.exists(get.path):
                return public.returnMsg(False,'The specified directory already exists!')
            os.makedirs(get.path)
            self.SetFileAccept(get.path);
            public.WriteLog('Document management','Create a directory ['+get.path+'] success!')
            return public.returnMsg(True,'Directory created successfully!')
        except:
            return public.returnMsg(False,'Directory creation failed!')

    def DeleteDir(self,get) :
        get.path = get.path.encode('utf-8');
        #if get.path.find('/opt/slemp/wwwroot') == -1: return public.returnMsg(False,'This is a demo server, it is forbidden to delete this directory!');
        if not os.path.exists(get.path):
            return public.returnMsg(False,'The specified directory does not exist!')

        if not self.CheckDir(get.path):
            return public.returnMsg(False,'Please don\'t die!');

        try:
            if os.path.exists(get.path+'/.user.ini'):
                os.system("chattr -i '"+get.path+"/.user.ini'")
            if hasattr(get,'empty'):
                if not self.delete_empty(get.path): return public.returnMsg(False,'Cannot delete non-empty directories !');

            if os.path.exists('data/recycle_bin.pl'):
                if self.Mv_Recycle_bin(get): return public.returnMsg(True,'The catalog has been moved to the recycle bin!');

            import shutil
            shutil.rmtree(get.path)
            public.WriteLog('Document management','Delete directory ['+get.path+'] success!')
            return public.returnMsg(True,'Directory deleted successfully!')
        except:
            return public.returnMsg(False,'Directory deletion failed!')

    def delete_empty(self,path):
        get.path = get.path.encode('utf-8');
        for files in os.listdir(path):
            return False
        return True

    def DeleteFile(self,get):
        get.path = get.path.encode('utf-8');
        #if get.path.find('/opt/slemp/wwwroot') == -1: return public.returnMsg(False,'This is a demo server, it is forbidden to delete this file!');
        if not os.path.exists(get.path):
            return public.returnMsg(False,'The specified file does not exist!')

        if get.path.find('.user.ini'):
            os.system("chattr -i '"+get.path+"'")
        try:
            if os.path.exists('data/recycle_bin.pl'):
                if self.Mv_Recycle_bin(get): return public.returnMsg(True,'Moved file to trash!');
            os.remove(get.path)
            public.WriteLog('Document management','Delete Files ['+get.path+'] success!')
            return public.returnMsg(True,'File deleted successfully!')
        except:
            return public.returnMsg(False,'File deletion failed!')

    def Mv_Recycle_bin(self,get):
        rPath = '/opt/slemp/Recycle_bin/'
        if not os.path.exists(rPath): os.system('mkdir -p ' + rPath);
        rFile = rPath + get.path.replace('/','_') + '_t_' + str(time.time());
        try:
            import shutil
            shutil.move(get.path, rFile)
            public.WriteLog('Document management','Move ['+get.path+'] successful at the recycle bin!')
            return True;
        except:
            public.WriteLog('Document management','Move ['+get.path+'] failed to recycle bin !')
            return False;

    def Re_Recycle_bin(self,get):
        rPath = '/opt/slemp/Recycle_bin/'
        get.path = get.path.encode('utf-8');
        dFile = get.path.replace('_','/').split('_t_')[0];
        get.path = rPath + get.path
        try:
            import shutil
            shutil.move(get.path, dFile)
            public.WriteLog('Document management','Recover from the recycle bin ['+dFile+'] success!')
            return public.returnMsg(True,'Successful recovery!');
        except:
            public.WriteLog('Document management','Recover from the recycle bin ['+dFile+'] failure!')
            return public.returnMsg(False,'Recovery failure!');

    def Get_Recycle_bin(self,get):
        rPath = '/opt/slemp/Recycle_bin/'
        if not os.path.exists(rPath): os.system('mkdir -p ' + rPath);
        data = {}
        data['dirs'] = []
        data['files'] = []
        data['status'] = os.path.exists('data/recycle_bin.pl')
        for file in os.listdir(rPath):
            tmp = {}
            fname = rPath + file
            tmp1 = file.split('_')
            tmp2 = tmp1[len(tmp1)-1].split('_t_')
            tmp['rname'] = file;
            tmp['dname'] = file.replace('_','/').split('_t_')[0]
            tmp['name'] = tmp2[0];
            tmp['time'] = int(float(tmp2[1]))
            tmp['size'] = os.path.getsize(fname)
            if os.path.isdir(fname):
                data['dirs'].append(tmp)
            else:
                data['files'].append(tmp)
        return data;

    def Del_Recycle_bin(self,get):
        rPath = '/opt/slemp/Recycle_bin/'
        get.path = get.path.encode('utf-8');

        if not self.CheckDir(rPath + get.path):
            return public.returnMsg(False,'Please don\'t die!');
        if os.path.isdir(rPath + get.path):
            import shutil
            shutil.rmtree(rPath + get.path)
        else:
            os.remove(rPath + get.path)

        tfile = get.path.replace('_','/').split('_t_')[0]
        public.WriteLog('Document management','Has been completely removed from the recycle bin ['+tfile+']')
        return public.returnMsg(True,'Has been completely removed from the recycle bin ['+tfile+']')

    def Close_Recycle_bin(self,get):
        rPath = '/opt/slemp/Recycle_bin/'
        os.system('rm -rf ' + rPath + '*');
        public.WriteLog('Document management','Empty the recycle bin successfully!');
        return public.returnMsg(True,'Empty recycle bin!');

    def Recycle_bin(self,get):
        c = 'data/recycle_bin.pl'
        if os.path.exists(c):
            os.remove(c)
            public.WriteLog('Document management','Turn off the recycle bin function successfully!');
            return public.returnMsg(True,'Recycle bin turned off!');
        else:
            public.writeFile(c,'True');
            public.WriteLog('Document management','Turn on the recycle bin function successfully!');
            return public.returnMsg(True,'Recycle bin function turned on!');

    def CopyFile(self,get) :
        get.sfile = get.sfile.encode('utf-8');
        get.dfile = get.dfile.encode('utf-8');
        if not os.path.exists(get.sfile):
            return public.returnMsg(False,'The specified file does not exist!')

        if os.path.isdir(get.sfile):
            return self.CopyDir(get)

        import shutil
        try:
            shutil.copyfile(get.sfile, get.dfile)
            public.WriteLog('Document management','Copy file ['+get.sfile+'] to ['+get.dfile+'] success!')
            self.SetFileAccept(get.dfile);
            return public.returnMsg(True,'File copy succeeded!')
        except:
            return public.returnMsg(False,'File copy failed!')

    def CopyDir(self,get):
        get.sfile = get.sfile.encode('utf-8');
        get.dfile = get.dfile.encode('utf-8');
        if not os.path.exists(get.sfile):
            return public.returnMsg(False,'The specified directory does not exist!')

        if not self.CheckDir(get.sfile):
            return public.returnMsg(False,'Please don\'t die!');

        import shutil
        try:
            shutil.copytree(get.sfile, get.dfile)
            public.WriteLog('Document management','Copy directory ['+get.sfile+'] to ['+get.dfile+'] success!')
            self.SetFileAccept(get.dfile);
            return public.returnMsg(True,'Directory replication succeeded!')
        except:
            return public.returnMsg(False,'Directory replication failed!')


    def MvFile(self,get) :
        get.sfile = get.sfile.encode('utf-8');
        get.dfile = get.dfile.encode('utf-8');
        if not os.path.exists(get.sfile):
            return public.returnMsg(False,'The specified file or directory does not exist!')

        if not self.CheckDir(get.sfile):
            return public.returnMsg(False,'Please don\'t die!');

        import shutil
        try:
            shutil.move(get.sfile, get.dfile)
            public.WriteLog('Document management','Moving files ['+get.sfile+'] to ['+get.dfile+'] success!')
            return public.returnMsg(True,'File move succeeded!')
        except:
            return public.returnMsg(False,'File or directory move failed!')


    def GetFileBody(self,get) :
        get.path = get.path.encode('utf-8');
        if not os.path.exists(get.path):
            return public.returnMsg(False,'The specified file does not exist!')
        #try:
        srcBody = public.readFile(get.path)

        data = {}
        if srcBody:
            import chardet
            char=chardet.detect(srcBody)
            data['encoding'] = char['encoding']
            if char['encoding'] == 'ascii':data['encoding'] = 'utf-8'
            data['data'] = srcBody.decode(char['encoding']).encode('utf-8')
        else:
            data['data'] = srcBody
            data['encoding'] = 'utf-8'

        data['status'] = True
        return data
        #except:
        #    return public.returnMsg(False,'File content acquisition failed, please check if the chardet component is installed.!')


    def SaveFileBody(self,get):
        get.path = get.path.encode('utf-8');
        if not os.path.exists(get.path):
            if get.path.find('.htaccess') == -1:
                return public.returnMsg(False,'The specified file does not exist!')

        try:
            isConf = get.path.find('.conf')
            if isConf != -1:
                os.system('\\cp -a '+get.path+' /tmp/backup.conf');

            data = get.data[0];
            if get.encoding == 'ascii':get.encoding = 'utf-8';
            public.writeFile(get.path,data.encode(get.encoding));


            if isConf != -1:
                isError = public.checkWebConfig();
                if isError != True:
                    os.system('\\cp -a /tmp/backup.conf '+get.path);
                    return public.returnMsg(False,'Configuration file error:<br><font style="color:red;">'+isError.replace("\n",'<br>')+'</font>');
                public.serviceReload();

            public.WriteLog('Document management','File ['+get.path+'] successfully saved!');
            return public.returnMsg(True,'File saved successfully!');
        except:
            return public.returnMsg(False,'File save failed!');

    def Zip(self,get) :
        get.sfile = get.sfile.encode('utf-8');
        get.dfile = get.dfile.encode('utf-8');
        get.path = get.path.encode('utf-8');
        if not os.path.exists(get.path+'/'+get.sfile):
                return public.returnMsg(False,'The specified file or directory does not exist');
        try:
            tmps = '/tmp/panelExec.log'
            if get.type == 'zip':
                os.system("cd '"+get.path+"' && zip '"+get.dfile+"' -r '"+get.sfile+"' > "+tmps+" 2>&1")
            else:
                os.system("cd '"+get.path+"' && tar -zcvf '"+get.dfile+"' '"+get.sfile+"' > "+tmps+" 2>&1")
            self.SetFileAccept(get.dfile);
            public.WriteLog("Document management", "Compressed file ["+get.sfile+"] to ["+get.dfile+"] success!");
            return public.returnMsg(True,'File compression succeeded!')
        except:
            return public.returnMsg(False,'File compression failed!')


    def UnZip(self,get):
        get.sfile = get.sfile.encode('utf-8');
        get.dfile = get.dfile.encode('utf-8');
        if not os.path.exists(get.sfile):
            return public.returnMsg(False,'The specified file or directory does not exist');
        #try:
        if not hasattr(get,'coding'): get.coding = 'UTF-8';
        tmps = '/tmp/panelExec.log'
        if get.type == 'zip':
            os.system("export LANG=\"zh_CN."+get.coding+"\" && unzip -o '"+get.sfile+"' -d '"+get.dfile+"' > "+tmps+" 2>&1")
        else:
            os.system("tar zxf '"+get.sfile+"' -C '"+get.dfile+"' > "+tmps+" 2>&1")
        self.SetFileAccept(get.dfile);
        public.WriteLog("Document management", "Unzip files ["+get.sfile+"] to ["+get.dfile+"] success!");
        return public.returnMsg(True,'File decompression succeeded!')
        #except:
        #    return public.returnMsg(False,'File decompression failed!')

    def GetFileAccess(self,get):
        get.filename = get.filename.encode('utf-8');
        data = {}
        try:
            import pwd
            stat = os.stat(get.filename)
            data['chmod'] = str(oct(stat.st_mode)[-3:])
            data['chown'] = pwd.getpwuid(stat.st_uid).pw_name
        except:
            data['chmod'] = 755
            data['chown'] = 'www'
        return data


    def SetFileAccess(self,get,all = '-R'):
        get.filename = get.filename.encode('utf-8');
        try:
            if not os.path.exists(get.filename):
                return public.returnMsg(False,'The specified file or directory does not exist!')
            os.system('chmod '+all+' '+get.access+" '"+get.filename+"'")
            os.system('chown '+all+' '+get.user+':'+get.user+" '"+get.filename+"'")
            public.WriteLog('Document management','Setting ['+get.filename+'] permission is ['+get.access+'], owner is ['+get.user+']')
            return public.returnMsg(True,'Permission setting is successful!')
        except:
            return public.returnMsg(False,'Permission setting failed!')

    def SetFileAccept(self,filename):
        os.system('chown -R www:www ' + filename)
        os.system('chmod -R 755 ' + filename)


    def GetDirSize(self,get):
        get.path = get.path.encode('utf-8');
        import web
        tmp = public.ExecShell('du -sbh '+ get.path)
        return tmp[0].split()[0]

    def CloseLogs(self,get):
        import web
        get.path = web.ctx.session.rootPath
        os.system('rm -f '+web.ctx.session.logsPath+'/*')
        if web.ctx.session.webserver == 'nginx':
            os.system('kill -USR1 `cat '+web.ctx.session.setupPath+'/nginx/logs/nginx.pid`');

        public.WriteLog('Document management','Clean up the website log successfully!')
        get.path = web.ctx.session.logsPath
        return self.GetDirSize(get)

    def SetBatchData(self,get):
        get.path = get.path.encode('utf-8');
        if get.type == '1' or get.type == '2':
            import web
            web.ctx.session.selected = get
            return public.returnMsg(True,'Mark successfully, please click the paste all button in the target directory!')
        elif get.type == '3':
            for key in get.data:
                try:
                    filename = get.path+'/'+key.encode('utf-8');
                    os.system('chmod -R '+get.access+" '"+filename+"'")
                    os.system('chown -R '+get.user+':'+get.user+" '"+filename+"'")
                except:
                    continue;
            public.WriteLog('Document management','Batch setting permissions succeeded!')
            return public.returnMsg(True,'Batch setting permissions succeeded!')
        else:

            import shutil
            isRecyle = os.path.exists('data/recycle_bin.pl')
            path = get.path
            for key in get.data:
                try:
                    filename = path + '/'+key.encode('utf-8');
                    get.path = filename;
                    if not os.path.exists(filename): continue
                    if os.path.isdir(filename):
                        if isRecyle:
                            self.Mv_Recycle_bin(get)
                        else:
                            shutil.rmtree(filename)
                    else:
                        if key == '.user.ini': os.system('chattr -i ' + filename);
                        if isRecyle:

                            self.Mv_Recycle_bin(get)
                        else:
                            os.remove(filename)
                except:
                    continue;

            public.WriteLog('Document management','Delete files successfully in batches!')
            return public.returnMsg(True,'Delete files successfully in batches!')


    def BatchPaste(self,get):
        import shutil,web
        i = 0;
        get.path = get.path.encode('utf-8');

        if get.type == '1':
            for key in web.ctx.session.selected.data:
                i += 1
                try:
                    sfile = web.ctx.session.selected.path + '/' + key.encode('utf-8')
                    dfile = get.path + '/' + key.encode('utf-8')
                    if os.path.isdir(sfile):
                        shutil.copytree(sfile,dfile)
                    else:
                        shutil.copyfile(sfile,dfile)
                except:
                    continue;
            public.WriteLog('Document management','From ['+web.ctx.session.selected.path+'] bulk copy to ['+get.path+'] success!!')
        else:
            for key in web.ctx.session.selected.data:
                try:
                    sfile = web.ctx.session.selected.path + '/' + key.encode('utf-8')
                    dfile = get.path + '/' + key.encode('utf-8')
                    shutil.move(sfile,dfile)
                    i += 1
                except:
                    continue;
            public.WriteLog('Document management','From ['+web.ctx.session.selected.path+'] move to batch ['+get.path+'] success!!')

        errorCount = len(web.ctx.session.selected.data) - i
        del(web.ctx.session.selected)
        return public.returnMsg(True,'Batch operation succeeded ['+str(i)+'], failure ['+str(errorCount)+']');

    def DownloadFile(self,get):
        get.path = get.path.encode('utf-8');
        import db,time
        isTask = '/tmp/panelTask.pl'
        execstr = get.url +'|bt|'+get.path+'/'+get.filename
        sql = db.Sql()
        sql.table('tasks').add('name,type,status,addtime,execstr',('download file ['+get.filename+']','download','0',time.strftime('%Y-%m-%d %H:%M:%S'),execstr))
        public.writeFile(isTask,'True')
        self.SetFileAccept(get.path+'/'+get.filename);
        public.WriteLog('Document management','Download file: ' + get.url + ' to '+ get.path);
        return public.returnMsg(True,'The download task has been added to the queue!')

    def InstallSoft(self,get):
        import db,time,web
        path = web.ctx.session.setupPath + '/php'
        if not os.path.exists(path): os.system("mkdir -p " + path);
        if web.ctx.session.server_os['x'] != 'RHEL': get.type = '3'
        public.writeFile('/var/slemp_setupPath.conf',web.ctx.session.rootPath)
        isTask = '/tmp/panelTask.pl'
        execstr = "cd " + web.ctx.session.setupPath + "/panel/script && /bin/bash install_soft.sh " + get.type + " install " + get.name + " "+ get.version;
        sql = db.Sql()
        if hasattr(get,'id'):
            id = get.id;
        else:
            id = None;
        sql.table('tasks').add('id,name,type,status,addtime,execstr',(None,'Install ['+get.name+'-'+get.version+']','execshell','0',time.strftime('%Y-%m-%d %H:%M:%S'),execstr))
        public.writeFile(isTask,'True')
        public.WriteLog('Installer','Add an installation task ['+get.name+'-'+get.version+'] success!');
        time.sleep(0.1);
        return public.returnMsg(True,'Installation task has been added to the queue');


    def RemoveTask(self,get):
        public.M('tasks').delete(get.id);
        return public.returnMsg(True,'Task deleted!');

    def ActionTask(self,get):
        isTask = '/tmp/panelTask.pl'
        public.writeFile(isTask,'True');
        return public.returnMsg(True,'Task queue is activated!');

    def UninstallSoft(self,get):
        import web
        public.writeFile('/var/slemp_setupPath.conf',web.ctx.session.rootPath)
        get.type = '0'
        if web.ctx.session.server_os['x'] != 'RHEL': get.type = '3'
        execstr = "cd " + web.ctx.session.setupPath + "/panel/script && /bin/bash install_soft.sh "+get.type+" uninstall " + get.name.lower() + " "+ get.version.replace('.','');
        os.system(execstr);
        public.WriteLog('Installer','Uninstall software ['+get.name+'-'+get.version+'] success!');
        return public.returnMsg(True,"Uninstall successfully!");


    def GetTaskSpeed(self,get):
        tempFile = '/tmp/panelExec.log'
        freshFile = '/tmp/panelFresh'
        if not os.path.exists(tempFile):
            return public.returnMsg(False,'Currently no task queue is executing-1!')
        import db
        find = db.Sql().table('tasks').where('status=?',('-1',)).field('id,type,name,execstr').find()
        if not len(find): return public.returnMsg(False,'There is currently no task queue executing-2!')
        echoMsg = {}
        echoMsg['name'] = find['name']
        echoMsg['execstr'] = find['execstr']
        if find['type'] == 'download':
            import json
            try:
                tmp = public.readFile(tempFile)
                if len(tmp) < 10:
                    return public.returnMsg(False,'There is currently no task queue executing-3!')
                echoMsg['msg'] = json.loads(tmp)
                echoMsg['isDownload'] = True
            except:
                db.Sql().table('tasks').where("id=?",(find['id'],)).save('status',('0',))
                return public.returnMsg(False,'There is currently no task queue executing-4!')
        else:
            echoMsg['msg'] = self.GetLastLine(tempFile,20)
            echoMsg['isDownload'] = False

        echoMsg['task'] = public.M('tasks').where("status!=?",('1',)).field('id,status,name,type').order("id asc").select()
        return echoMsg

    def GetLastLine(self,inputfile,lineNum):
        try:
            fp = open(inputfile, 'r')
            lastLine = ""

            lines =  fp.readlines()
            count = len(lines)
            if count>lineNum:
                num=lineNum
            else:
                num=count
            i=1;
            lastre = []
            for i in range(1,(num+1)):
                if lines :
                    n = -i
                    lastLine = lines[n].strip()
                    fp.close()
                    lastre.append(lastLine)

            result = ''
            lineNum -= 1
            while lineNum > 0:
                result += lastre[lineNum]+"\n"
                lineNum -= 1

            return result
        except:
            return "Menunggu eksekusi ..."
