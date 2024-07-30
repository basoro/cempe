#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=en_US.UTF-8

sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*
sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*

echo "
+---------------------------------+
| CEMPe Panel 1.x  Untuk CentOS 7 |
+---------------------------------+
"
download_Url=http://basoro.id/downloads/slemp

setup_path=/opt/slemp
port='7777'

while [ "$go" != 'y' ] && [ "$go" != 'n' ]
do
	read -p "Yakin mau memasang CEMPe Panel?(y/n): " go;
done

if [ "$go" == 'n' ];then
	exit;
fi

startTime=`date +%s`
php_version="81"
vphp="8.1"

setenforce 0
sed -i 's/SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config
yum install epel-release -y
#yum update -y
for pace in wget python-pip python-devel python-imaging gcc zip unzip;
do yum -y install $pace; done
sleep 5

wget -O setuptools-33.1.1.zip https://files.pythonhosted.org/packages/dc/8c/7c9869454bdc53e72fb87ace63eac39336879eef6f2bf96e946edbf03e90/setuptools-33.1.1.zip -T 10
unzip setuptools-33.1.1.zip
rm -f setuptools-33.1.1.zip
cd setuptools-33.1.1
python setup.py install
cd ..
rm -rf setuptools-33.1.1

wget -O psutil-5.2.2.tar.gz https://files.pythonhosted.org/packages/57/93/47a2e3befaf194ccc3d05ffbcba2cdcdd22a231100ef7e4cf63f085c900b/psutil-5.2.2.tar.gz -T 10
tar xvf psutil-5.2.2.tar.gz
rm -f psutil-5.2.2.tar.gz
cd psutil-5.2.2
python setup.py install
cd ..
rm -rf psutil-5.2.2

wget -O chardet-2.3.0.tar.gz https://files.pythonhosted.org/packages/7d/87/4e3a3f38b2f5c578ce44f8dc2aa053217de9f0b6d737739b0ddac38ed237/chardet-2.3.0.tar.gz -T 10
tar xvf chardet-2.3.0.tar.gz
rm -f chardet-2.3.0.tar.gz
cd chardet-2.3.0
python setup.py install
cd ..
rm -rf chardet-2.3.0

wget --no-check-certificate -O web.py-0.38.tar.gz https://webpy.org/static/web.py-0.38.tar.gz -T 10
tar xvf web.py-0.38.tar.gz
rm -f web.py-0.38.tar.gz
cd web.py-0.38
python setup.py install
cd ..
rm -rf web.py-0.38

mkdir -p /opt/slemp/server

mkdir -pv /opt/slemp/{wwwroot/default,wwwlogs,server/{data,nginx/{sbin,logs,conf/{vhost,rewrite}},php/$php_version/{etc,bin,sbin,var/run}}}

wget -O panel.zip https://github.com/basoro/cempe/archive/master.zip

unzip -o panel.zip -d $setup_path/server/ > /dev/null
mv $setup_path/server/cempe-master $setup_path/server/panel

python -m compileall $setup_path/server/panel
rm -f $setup_path/server/panel/*.py

chmod 777 /tmp
mv $setup_path/server/panel/scripts/slemp.init /etc/init.d/slemp
chmod +x /etc/init.d/slemp

chkconfig --add slemp
chkconfig --level 2345 slemp on

chmod -R 600 $setup_path/server/panel
ln -sf /etc/init.d/slemp /usr/bin/slemp
echo "$port" > $setup_path/server/panel/data/port.pl
rm -f $setup_path/server/panel/data/default.db
sqlite3 $setup_path/server/panel/data/default.db < $setup_path/server/panel/data/default.sql
/etc/init.d/slemp start
password=`cat /dev/urandom | head -n 16 | md5sum | head -c 8`
cd $setup_path/server/panel/
username=`python tools.pyc panel $password`
cd ~
rm -f panel.zip
echo "$password" > $setup_path/server/panel/default.pl
chmod 600 $setup_path/server/panel/default.pl

yum install firewalld -y
systemctl enable firewalld
systemctl start firewalld
firewall-cmd --set-default-zone=public > /dev/null 2>&1
firewall-cmd --permanent --zone=public --add-port=22/tcp > /dev/null 2>&1
firewall-cmd --permanent --zone=public --add-port=80/tcp > /dev/null 2>&1
firewall-cmd --permanent --zone=public --add-port=443/tcp > /dev/null 2>&1
firewall-cmd --permanent --zone=public --add-port=3306/tcp > /dev/null 2>&1
firewall-cmd --permanent --zone=public --add-port=777/tcp > /dev/null 2>&1
firewall-cmd --permanent --zone=public --add-port=$port/tcp > /dev/null 2>&1
firewall-cmd --reload

systemctl stop httpd
systemctl disable httpd
systemctl stop xinetd
systemctl disable xinetd
systemctl stop saslauthd
systemctl disable saslauthd
systemctl stop sendmail
systemctl disable sendmail
systemctl stop rsyslog
systemctl disable rsyslog

groupadd www
useradd -s /sbin/nologin -g www www

yum -y remove httpd php rsyslog sendmail postfix

rpm -Uvh http://nginx.org/packages/rhel/7/noarch/RPMS/nginx-release-rhel-7-0.el7.ngx.noarch.rpm
rpm -Uvh http://rpms.famillecollet.com/enterprise/remi-release-7.rpm

yum -y install nginx
yum -y install postfix syslog-ng cronie libdbi libdbi-drivers syslog-ng-libdbi zip unzip glibc.i686

###################
# Configure nginx #
###################

cat > /opt/slemp/server/nginx/conf/pathinfo.conf <<END
set \$real_script_name \$fastcgi_script_name;
if (\$fastcgi_script_name ~ "^(.+?\.php)(/.+)$") {
set \$real_script_name \$1;
set \$path_info \$2;
}
fastcgi_param SCRIPT_FILENAME \$document_root\$real_script_name;
fastcgi_param SCRIPT_NAME \$real_script_name;
fastcgi_param PATH_INFO \$path_info;
END

cat > /etc/nginx/nginx.conf <<END
user  www www;
worker_processes auto;
error_log  /opt/slemp/wwwlogs/nginx_error.log  crit;
pid        /opt/slemp/server/nginx/logs/nginx.pid;
worker_rlimit_nofile 51200;

events
    {
        use epoll;
        worker_connections 51200;
        multi_accept on;
    }

http
    {
        include       mime.types;
        default_type  application/octet-stream;

        server_names_hash_bucket_size 512;
        client_header_buffer_size 32k;
        large_client_header_buffers 4 32k;
        client_max_body_size 50m;

        sendfile   on;
        tcp_nopush on;

        keepalive_timeout 60;

        tcp_nodelay on;

        fastcgi_connect_timeout 300;
        fastcgi_send_timeout 300;
        fastcgi_read_timeout 300;
        fastcgi_buffer_size 64k;
        fastcgi_buffers 4 64k;
        fastcgi_busy_buffers_size 128k;
        fastcgi_temp_file_write_size 256k;
        fastcgi_intercept_errors on;

        gzip on;
        gzip_min_length  1k;
        gzip_buffers     4 16k;
        gzip_http_version 1.1;
        gzip_comp_level 2;
        gzip_types     text/plain application/javascript application/x-javascript text/javascript text/css application/xml;
        gzip_vary on;
        gzip_proxied   expired no-cache no-store private auth;
        gzip_disable   "MSIE [1-6]\.";

        server_tokens off;
        access_log off;
        server {
            listen 80 default;
            server_name _;
            index index.html index.htm index.php;
            root /opt/slemp/wwwroot/default;
            try_files \$uri \$uri/ @handler;
            location  /admin {
                try_files \$uri \$uri/ /admin/index.php?\$args;
            }
            location @handler {
                if (!-e \$request_filename) { rewrite / /index.php last; }
                rewrite ^(.*.php)/ \$1 last;
            }
            include enable-php-${php_version}.conf;
        }
				server{
            listen 777;
            server_name phpmyadmin.basoro.id;
            index index.html index.htm index.php;
            root  /opt/slemp/server/phpmyadmin;
            include enable-php-${php_version}.conf;
        }
    include /opt/slemp/server/nginx/conf/vhost/*.conf;
}
END

rm -rf /etc/nginx/conf.d/*

rm -f /etc/init.d/nginx
mv $setup_path/server/panel/scripts/nginx.init /etc/init.d/nginx
chmod +x /etc/init.d/nginx
ln -sf /usr/sbin/nginx /opt/slemp/server/nginx/sbin/nginx
ln -sf /etc/nginx/nginx.conf /opt/slemp/server/nginx/conf/nginx.conf
ln -sf /etc/nginx/mime.types /opt/slemp/server/nginx/conf/mime.types
ln -sf /etc/nginx/fastcgi_params /opt/slemp/server/nginx/conf/fastcgi_params
ln -sf /opt/slemp/server/nginx/conf/pathinfo.conf /etc/nginx/pathinfo.conf
touch /opt/slemp/server/nginx/conf/enable-php${php_version}.conf
ln -sf /opt/slemp/server/nginx/conf/enable-php-${php_version}.conf /etc/nginx/enable-php-${php_version}.conf
ln -s /opt/slemp/server/nginx/conf/rewrite /etc/nginx/rewrite
ln -s /opt/slemp/server/nginx/conf/key /etc/nginx/key

command="nginx -v"
nginxv=$( ${command} 2>&1 )
nginxlocal=$(echo $nginxv | grep -o '[0-9.]*$')
echo $nginxlocal > /opt/slemp/server/nginx/version.pl


#php_version="56";
yum -y install php${php_version}-php-common php${php_version}-php-fpm php${php_version}-php-process php${php_version}-php-mysql php${php_version}-php-pecl-memcache php${php_version}-php-pecl-memcached php${php_version}-php-gd php${php_version}-php-mbstring php${php_version}-php-mcrypt php${php_version}-php-xml php${php_version}-php-pecl-apc php${php_version}-php-cli php${php_version}-php-pear php${php_version}-php-pdo

cat > /opt/slemp/server/nginx/conf/enable-php-${php_version}.conf <<END
location ~ [^/]\.php(/|$)
{
    try_files \$uri =404;
    fastcgi_pass  unix:/tmp/php-cgi-${php_version}.sock;
    fastcgi_index index.php;
    include /etc/nginx/fastcgi_params;
    include pathinfo.conf;
}
END

ln -sf /opt/slemp/server/nginx/conf/enable-php-${php_version}.conf /etc/nginx/enable-php-${php_version}.conf
php_conf="/etc/opt/remi/php${php_version}"
#vphp="5.6";

yum -y install php81-php-pecl-zip

echo "Write Zip Extension to php.ini..."
cat >> ${php_conf}/php.ini <<EOF

;Zip
extension=/opt/remi/php${php_version}/root/usr/lib64/php/modules/zip.so

EOF

sed -i 's/upload_max_filesize = 2M/upload_max_filesize = 100M/' ${php_conf}/php.ini
sed -i 's/post_max_size = 8M/post_max_size = 100M/' ${php_conf}/php.ini
ln -s ${php_conf}/php.ini /opt/slemp/server/php/${php_version}/etc/php.ini

cat > ${php_conf}/php-fpm.d/www.conf <<END
[www]
listen = /tmp/php-cgi-${php_version}.sock
listen.allowed_clients = 127.0.0.1
listen.owner = www
listen.group = www
listen.mode = 0666
user = www
group = www
pm = dynamic
pm.status_path = /phpfpm_${php_version}_status
pm.process_idle_timeout = 3s
pm.max_children = 50
pm.start_servers = 10
pm.min_spare_servers = 10
pm.max_spare_servers = 50
pm.max_requests = 500
php_admin_value[error_log] = /var/log/php-fpm/www-error.log
php_admin_flag[log_errors] = on
php_admin_value[upload_max_filesize] = 32M
END

ln -sf /opt/remi/php${php_version}/root/usr/bin/php /opt/slemp/server/php/${php_version}/bin/php
ln -sf /opt/remi/php${php_version}/root/usr/bin/phpize /opt/slemp/server/php/${php_version}/bin/phpize
ln -sf /opt/remi/php${php_version}/root/usr/bin/pear /opt/slemp/server/php/${php_version}/bin/pear
ln -sf /opt/remi/php${php_version}/root/usr/bin/pecl /opt/slemp/server/php/${php_version}/bin/pecl
ln -sf /opt/remi/php${php_version}/root/usr/sbin/php-fpm /opt/slemp/server/php/${php_version}/sbin/php-fpm
ln -sf /etc/opt/remi/php${php_version}/php.ini /etc/php.ini
echo "${php_version}" > $setup_path/server/php/${php_version}/version.pl

rm -f /etc/init.d/php-fpm
mv $setup_path/server/panel/scripts/php-fpm.init /etc/init.d/php-fpm
chmod +x /etc/init.d/php-fpm

chkconfig syslog-ng on
service syslog-ng start
chkconfig crond on
service crond start
chkconfig nginx on
chkconfig php-fpm on

/etc/init.d/nginx start
/etc/init.d/php-fpm start

echo '<span style="color:green" class="glyphicon glyphicon-play"></span>' > /opt/slemp/server/panel/data/status-nginx.pl
echo '<span style="color:green" class="glyphicon glyphicon-play"></span>' > /opt/slemp/server/panel/data/status-php-fpm.pl

chown -R www:www /opt/slemp/wwwroot/default/
chown -R www:www /opt/slemp/server/panel/

cat > /opt/slemp/wwwroot/default/index.php <<END
<?php
phpinfo();
?>
END

#Fix Sessions:
mkdir -p /var/lib/php/session
chmod 777 /var/lib/php/session
#rm -rf $setup_path/server/panel/scripts
sleep 3

cd ~

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

sed -i "s,localhost/mlite,${address},g" /opt/slemp/wwwroot/default/config.php

echo -e "=================================================================="
echo -e "\033[32mSelamat! Pemasangan CEMPe Panel berhasil!\033[0m"
echo -e "=================================================================="
echo  "CEMPe-Panel: http://$address:$port"
echo -e "Panel Username: $username"
echo -e "Panel Password: $password"
echo -e "Default Url: http://$address"
echo -e "\033[33mPeringatan:\033[0m"
echo -e "\033[33mJika tidak bisa mengakses panel, \033[0m"
echo -e "\033[33msilahkan buka port berikut (7777|777|80|22)\033[0m"
echo -e "=================================================================="

endTime=`date +%s`
((outTime=($endTime-$startTime)/60))
echo -e "Waktu :\033[32m $outTime \033[0mMenit!"
