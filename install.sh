#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=en_US.UTF-8

echo "
+----------------------------
| Panel Lite 1.x  Setup FOR CentOS
+----------------------------
"
download_Url=https://basoro.id/downloads/slemp

setup_path=/opt/slemp
port='12345'

while [ "$go" != 'y' ] && [ "$go" != 'n' ]
do
	read -p "Do you want to install SLEMP-Panel to the $setup_path directory now?(y/n): " go;
done

if [ "$go" == 'n' ];then
	exit;
fi

startTime=`date +%s`

setenforce 0
sed -i 's/SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config
yum install epel-release -y
for pace in wget unzip python-pip python-devel python-imaging zip unzip;
do yum -y install $pace; done
sleep 5

pip install --upgrade pip
pip install --upgrade setuptools
pip install psutil chardet web.py pillow

mkdir -p /opt/slemp/server

wget -O panel.zip https://github.com/basoro/panel/archive/master.zip
wget -O /etc/init.d/slemp $download_Url/init/slemp.init -T 10

unzip -o master.zip -d $setup_path/server/ > /dev/null
mv $setup_path/server/panel-master $setup_path/server/panel

python -m compileall $setup_path/server/panel
rm -f $setup_path/server/panel/class/*.py
rm -f $setup_path/server/panel/*.py

chmod 777 /tmp
chmod +x /etc/init.d/slemp

if [ -f "/usr/sbin/update-rc.d" ];then
	update-rc.d slemp defaults
else
	chkconfig --add slemp
	chkconfig --level 2345 slemp on
fi

chmod -R 600 $setup_path/server/panel
chmod -R +x $setup_path/server/panel/script
ln -sf /etc/init.d/slemp /usr/bin/slemp
echo "$port" > $setup_path/server/panel/data/port.pl
/etc/init.d/slemp start
password=`cat /dev/urandom | head -n 16 | md5sum | head -c 8`
cd $setup_path/server/panel/
username=`python tools.pyc panel $password`
cd ~
echo "$password" > $setup_path/server/panel/default.pl
chmod 600 $setup_path/server/panel/default.pl

if [ -f "/etc/init.d/iptables" ];then
  iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 22 -j ACCEPT
  iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT
  iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 1234 -j ACCEPT
  iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport $port -j ACCEPT
  iptables -A INPUT -p icmp --icmp-type any -j ACCEPT
  iptables -A INPUT -s localhost -d localhost -j ACCEPT
  iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
  iptables -P INPUT DROP
  service iptables save
  service iptables restart
fi

if [ "${isVersion}" == '' ];then
  if [ ! -f "/etc/init.d/iptables" ];then
    yum install firewalld -y
    systemctl enable firewalld
    systemctl start firewalld
    firewall-cmd --set-default-zone=public > /dev/null 2>&1
    firewall-cmd --permanent --zone=public --add-port=22/tcp > /dev/null 2>&1
    firewall-cmd --permanent --zone=public --add-port=80/tcp > /dev/null 2>&1
    firewall-cmd --permanent --zone=public --add-port=1234/tcp > /dev/null 2>&1
    firewall-cmd --permanent --zone=public --add-port=$port/tcp > /dev/null 2>&1
    firewall-cmd --reload
  fi
fi

address=""
n=0
while [ "$address" == '' ]
do
	address=`curl ifconfig.me`
	let n++
	sleep 0.1
	if [ $n -gt 5 ];then
		address="SERVER_IP"
	fi
done

echo -e "=================================================================="
echo -e "\033[32mCongratulations! Install succeeded!\033[0m"
echo -e "=================================================================="
echo  "SLEMP-Panel: http://$address:$port"
echo -e "username: $username"
echo -e "password: $password"
echo -e "\033[33mWarning:\033[0m"
echo -e "\033[33mIf you cannot access the panel, \033[0m"
echo -e "\033[33mrelease the following port (12345|1234|80|22) in the security group\033[0m"
echo -e "=================================================================="

endTime=`date +%s`
((outTime=($endTime-$startTime)/60))
echo -e "Time consumed:\033[32m $outTime \033[0mMinute!"
