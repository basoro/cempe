#!/bin/bash

###################
# disable selinux #
###################
setenforce 0
sed -i 's/SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config

startTime=`date +%s`

##############################
# disable un-needed services #
##############################
systemctl stop httpd
systemctl disable httpd
systemctl stop xinetd
chkcsystemctl disableonfig xinetd
systemctl stop saslauthd
systemctl disable saslauthd
systemctl stop sendmail
systemctl disable sendmail
systemctl stop rsyslog
systemctl disable rsyslog

groupadd www
useradd -s /sbin/nologin -g www www

#Create directories
mkdir -pv /opt/slemp/{wwwroot/default,wwwlogs,server/{mysql/{bin,lib},nginx/{sbin,logs,conf/{vhost,rewrite}}}}

#remove all current PHP, MySQL, mailservers, rsyslog.
yum -y remove httpd php mysql rsyslog sendmail postfix mysql-libs

###################
# Add a few repos #
###################

# nginx repo
rpm -Uvh http://nginx.org/packages/rhel/7/noarch/RPMS/nginx-release-rhel-7-0.el7.ngx.noarch.rpm

# epel-release repo
yum -y install epel-release

# mysql 5.6 repo
rpm -Uvh http://repo.mysql.com/mysql-community-release-el7-5.noarch.rpm

################################
# Install NGINX and MySQL #
################################

yum -y install nginx

yum -y install mysql-community-server

#####################################################
# Install Postfix, SyLog-Ng, Cronie and Other Stuff #
#####################################################

yum -y install postfix syslog-ng cronie wget libdbi libdbi-drivers libdbi-dbd-mysql syslog-ng-libdbi zip unzip glibc.i686


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
    include /opt/slemp/server/nginx/conf/vhost/*.conf;
}
END
rm -rf /etc/nginx/conf.d/*

rm -f /etc/init.d/nginx
wget -O /etc/init.d/nginx https://raw.githubusercontent.com/basoro/basoro.github.io/master/downloads/slemp/init/nginx.init -T20
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
systemctl start mysqld
sleep 5
/usr/bin/mysqladmin -u root password 'root'
/opt/slemp/server/mysql/bin/mysql -uroot -proot -e "SET PASSWORD FOR 'root'@'localhost' = PASSWORD('${mysqlpwd}')"
/opt/slemp/server/mysql/bin/mysql -uroot -p${mysqlpwd} -e "SET PASSWORD FOR 'root'@'127.0.0.1' = PASSWORD('${mysqlpwd}')"
/opt/slemp/server/mysql/bin/mysql -uroot -p${mysqlpwd} -e "flush privileges"


token=${pwd:0:8}
echo "${token}" > /opt/slemp/server/token.pl

#start services and configure iptables
yum -y install firewalld
systemctl enable firewalld
systemctl start firewalld
firewall-cmd --permanent --zone=public --add-port=80/tcp
firewall-cmd --reload

chkconfig syslog-ng on
service syslog-ng start
chkconfig crond on
service crond start
service nginx restart
chkconfig nginx on
service mysqld start
chkconfig mysqld on

chown -R www:www /opt/slemp/wwwroot/default/


sleep 3

cd ~

clear
echo
echo
echo "====================================="
echo -e "\033[32mInstalasi server selesai.\033[0m"
echo -e "====================================="
echo Default Site Url: http://SERVER_IP
echo MySQL Password: $mysqlpwd
echo -e "====================================="
endTime=`date +%s`
((outTime=($endTime-$startTime)/60))
echo -e "Time consuming:\033[32m $outTime \033[0mMinute!"
echo
echo
echo
exit
