#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=en_US.UTF-8

echo "
+-------------------------------------
| SLEMP Panel Lite 1.x  Untuk CentOS 7
+-------------------------------------
"
download_Url=https://basoro.id/downloads/slemp

setup_path=/opt/slemp
port='12345'

while [ "$go" != 'y' ] && [ "$go" != 'n' ]
do
	read -p "Yakin mau memasang SLEMP Panel Lite?(y/n): " go;
done

if [ "$go" == 'n' ];then
	exit;
fi

startTime=`date +%s`

setenforce 0
sed -i 's/SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config
yum install epel-release -y
for pace in wget python-pip python-devel python-imaging gcc zip unzip;
do yum -y install $pace; done
sleep 5

pip install --upgrade pip
pip install --upgrade setuptools
pip install wheel
pip install psutil chardet web.py==0.51 pillow

mkdir -p /opt/slemp/server

mkdir -pv /opt/slemp/{wwwroot/default,wwwlogs,server/{data,mysql/{bin,lib},nginx/{sbin,logs,conf/{vhost,rewrite}},php/56/{etc,bin,sbin,var/run}}}

wget -O panel.zip https://github.com/basoro/panel/archive/master.zip

unzip -o panel.zip -d $setup_path/server/ > /dev/null
mv $setup_path/server/panel-master $setup_path/server/panel

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
firewall-cmd --permanent --zone=public --add-port=1234/tcp > /dev/null 2>&1
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

yum -y remove httpd php mysql rsyslog sendmail postfix mysql-libs

rpm -Uvh http://nginx.org/packages/rhel/7/noarch/RPMS/nginx-release-rhel-7-0.el7.ngx.noarch.rpm
rpm -Uvh http://repo.mysql.com/mysql-community-release-el7-5.noarch.rpm
rpm -Uvh http://rpms.famillecollet.com/enterprise/remi-release-7.rpm

yum -y install nginx
yum -y install mysql-community-server
yum -y install postfix syslog-ng cronie libdbi libdbi-drivers libdbi-dbd-mysql syslog-ng-libdbi zip unzip glibc.i686

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
        include enable-php-56.conf;
    }
		server{
        listen 1234;
        server_name phpmyadmin.basoro.id;
        index index.html index.htm index.php;
        root  /opt/slemp/server/phpmyadmin;
        include enable-php-56.conf;
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
touch /opt/slemp/server/nginx/conf/enable-php-56.conf
ln -sf /opt/slemp/server/nginx/conf/enable-php-56.conf /etc/nginx/enable-php-56.conf
ln -s /opt/slemp/server/nginx/conf/rewrite /etc/nginx/rewrite
ln -s /opt/slemp/server/nginx/conf/key /etc/nginx/key

command="nginx -v"
nginxv=$( ${command} 2>&1 )
nginxlocal=$(echo $nginxv | grep -o '[0-9.]*$')
echo $nginxlocal > /opt/slemp/server/nginx/version.pl

########################
# install MySQL config #
########################

rm -f /etc/my.cnf
cat > /etc/my.cnf<<EOF
[client]
#password       = your_password
port            = 3306
socket          = /var/lib/mysql/mysql.sock

[mysqld]
port            = 3306
socket          = /var/lib/mysql/mysql.sock
datadir = /opt/slemp/server/data
#default_storage_engine = MyISAM
#skip-external-locking
#loose-skip-innodb
key_buffer_size = 16M
max_allowed_packet = 1M
table_open_cache = 64
sort_buffer_size = 512K
net_buffer_length = 8K
read_buffer_size = 256K
read_rnd_buffer_size = 512K
myisam_sort_buffer_size = 8M
thread_cache_size = 8
query_cache_size = 8M
tmp_table_size = 16M

#skip-networking
max_connections = 500
max_connect_errors = 100
open_files_limit = 65535

log-bin=mysql-bin
binlog_format=mixed
server-id       = 1
expire_logs_days = 10

default_storage_engine = InnoDB
innodb_data_home_dir = /opt/slemp/server/data
innodb_data_file_path = ibdata1:10M:autoextend
innodb_log_group_home_dir = /opt/slemp/server/data
innodb_buffer_pool_size = 8M
innodb_additional_mem_pool_size = 1M
innodb_log_file_size = 2M
innodb_log_buffer_size = 4M
innodb_flush_log_at_trx_commit = 1
innodb_lock_wait_timeout = 50

[mysqldump]
quick
max_allowed_packet = 16M

[mysql]
no-auto-rehash

[myisamchk]
key_buffer_size = 20M
sort_buffer_size = 20M
read_buffer = 2M
write_buffer = 2M

[mysqlhotcopy]
interactive-timeout
EOF


## Ini belum fix
ln -sf /usr/bin/mysql /opt/slemp/server/mysql/bin/mysql
ln -sf /usr/bin/mysqldump /opt/slemp/server/mysql/bin/mysqldump
ln -sf /usr/bin/myisamchk /opt/slemp/server/mysql/bin/myisamchk
ln -sf /usr/bin/mysqld_safe /opt/slemp/server/mysql/bin/mysqld_safe
ln -sf /usr/bin/mysqlcheck /opt/slemp/server/mysql/bin/mysqlcheck
ln -s /usr/lib64/mysql/libmysqlclient.so.18 /opt/slemp/server/mysql/lib/libmysqlclient.so
ln -s /usr/lib64/mysql/libmysqlclient.so.18 /opt/slemp/server/mysql/lib/libmysqlclient.so.18
ln -sf /var/lib/mysql/mysql.sock /tmp/mysql.sock
echo "5.6" > /opt/slemp/server/mysql/version.pl
chown -R mysql:mysql /opt/slemp/server/data/rm -f /etc/init.d/mysqld
mv $setup_path/server/panel/scripts/mysqld.init /etc/init.d/mysqld
chmod +x /etc/init.d/mysqld
systemctl start mysql
mysqlpwd=`cat /dev/urandom | head -n 16 | md5sum | head -c 8`
/usr/bin/mysqladmin -u root password 'root'
/opt/slemp/server/mysql/bin/mysql -uroot -proot -e "SET PASSWORD FOR 'root'@'localhost' = PASSWORD('${mysqlpwd}')"
/opt/slemp/server/mysql/bin/mysql -uroot -p${mysqlpwd} -e "SET PASSWORD FOR 'root'@'127.0.0.1' = PASSWORD('${mysqlpwd}')"
/opt/slemp/server/mysql/bin/mysql -uroot -p${mysqlpwd} -e "flush privileges"
echo "$mysqlpwd" > $setup_path/server/mysql/default.pl
chmod 600 $setup_path/server/mysql/default.pl

php_version="56";
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
php_conf="/opt/remi/php${php_version}/root/etc"
vphp="5.6";

mkdir /usr/local/ioncube
wget -O /usr/local/ioncube/ioncube_loader_lin_${vphp}.so https://basoro.id/downloads/ioncube_loader_lin_${vphp}.so -T 20

echo "Write Ioncube Loader to php.ini..."
cat >> ${php_conf}/php.ini <<EOF

;ionCube
zend_extension = /usr/local/ioncube/ioncube_loader_lin_${vphp}.so

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
ln -sf /opt/remi/php${php_version}/root/etc/php.ini /etc/php.ini
echo "5.6" > $setup_path/server/php/56/version.pl

rm -f /etc/init.d/php-fpm
mv $setup_path/server/panel/scripts/php-fpm.init /etc/init.d/php-fpm
chmod +x /etc/init.d/php-fpm

wget -O phpMyAdmin.zip $download_Url/src/phpMyAdmin-4.4.zip -T20

unzip -o phpMyAdmin.zip -d $setup_path/server/phpmyadmin/ > /dev/null
rm -f phpMyAdmin.zip
rm -rf $setup_path/server/phpmyadmin/phpmyadmin*

phpmyadminExt=`cat /dev/urandom | head -n 32 | md5sum | head -c 16`;
mv $setup_path/server/phpmyadmin/databaseAdmin $setup_path/server/phpmyadmin/phpmyadmin_$phpmyadminExt
chmod -R 744 $setup_path/server/phpmyadmin/phpmyadmin_$phpmyadminExt
chown -R www.www $setup_path/server/phpmyadmin/phpmyadmin_$phpmyadminExt

secret=`cat /dev/urandom | head -n 32 | md5sum | head -c 32`;
\cp -a -r $setup_path/server/phpmyadmin/phpmyadmin_$phpmyadminExt/config.sample.inc.php  $setup_path/server/phpmyadmin/phpmyadmin_$phpmyadminExt/config.inc.php
sed -i "s#^\$cfg\['blowfish_secret'\].*#\$cfg\['blowfish_secret'\] = '${secret}';#" $setup_path/server/phpmyadmin/phpmyadmin_$phpmyadminExt/libraries/config.default.php
sed -i "s#^\$cfg\['blowfish_secret'\].*#\$cfg\['blowfish_secret'\] = '${secret}';#" $setup_path/server/phpmyadmin/phpmyadmin_$phpmyadminExt/config.inc.php

echo "4.4" > $setup_path/server/phpmyadmin/version.pl
echo $phpmyadminExt > $setup_path/server/phpmyadmin/default.pl


chkconfig syslog-ng on
service syslog-ng start
chkconfig crond on
service crond start
chkconfig nginx on
chkconfig php-fpm on
systemctl stop mysql
chkconfig mysqld on

chown -R www:www /opt/slemp/wwwroot/default/
chown -R www:www /opt/slemp/server/panel/

#Fix Sessions:
mkdir -p /var/lib/php/session
chmod 777 /var/lib/php/session
rm -rf $setup_path/server/panel/scripts
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

echo -e "=================================================================="
echo -e "\033[32mSelamat! Pemasangan SLEMP Panel Lite berhasil!\033[0m"
echo -e "=================================================================="
echo  "SLEMP-Panel: http://$address:$port"
echo -e "username: $username"
echo -e "password: $password"
echo -e "Default Site Url: http://$address"
echo -e "MySQL Password: $mysqlpwd"
echo -e "\033[33mPeringatan:\033[0m"
echo -e "\033[33mJika tidak bisa mengakses panel, \033[0m"
echo -e "\033[33msilahkan buka port berikut (12345|1234|80|22) di menu keamanan\033[0m"
echo -e "=================================================================="

endTime=`date +%s`
((outTime=($endTime-$startTime)/60))
echo -e "Waktu :\033[32m $outTime \033[0mMenit!"
