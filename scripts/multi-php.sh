#!/bin/bash

rpm -Uvh http://rpms.famillecollet.com/enterprise/remi-release-7.rpm

Install_PHP() 
{
mkdir -pv /opt/slemp/server/php/${php_version}/{etc,bin,sbin,var/run}

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
  
#install php-fpm config 
if [ "${php_version}" = "54" ];then
  php_conf="/opt/remi/php${php_version}/root/etc" 
fi
if [ "${php_version}" = "55" ];then
  php_conf="/opt/remi/php${php_version}/root/etc" 
fi
if [ "${php_version}" = "56" ];then
  php_conf="/opt/remi/php${php_version}/root/etc" 
fi
if [ "${php_version}" = "70" ];then
  php_conf="/etc/opt/remi/php${php_version}" 
fi
if [ "${php_version}" = "71" ];then
  php_conf="/etc/opt/remi/php${php_version}" 
fi
if [ "${php_version}" = "72" ];then
  php_conf="/etc/opt/remi/php${php_version}" 
fi
if [ "${php_version}" = "73" ];then
  php_conf="/etc/opt/remi/php${php_version}" 
fi
if [ "${php_version}" = "74" ];then
  php_conf="/etc/opt/remi/php${php_version}" 
fi
if [ "${php_version}" = "80" ];then
  php_conf="/etc/opt/remi/php${php_version}" 
fi
if [ "${php_version}" = "81" ];then
  php_conf="/etc/opt/remi/php${php_version}" 
fi
if [ "${php_version}" = "82" ];then
  php_conf="/etc/opt/remi/php${php_version}" 
fi

#wget -O /usr/local/ioncube/ioncube_loader_lin_${vphp}.so basoro.id/downloads/ioncube_loader_lin_${vphp}.so -T 20

#wget https://downloads.ioncube.com/loader_downloads/ioncube_loaders_lin_x86-64.tar.gz
#tar -xvf ioncube_loaders_lin_x86-64.tar.gz -C /usr/local

if [ "$vphp" != "8.0" ]
then
echo "Write Ioncube Loader to php.ini..."
cat >> ${php_conf}/php.ini <<EOF

;ionCube
zend_extension = /usr/local/ioncube/ioncube_loader_lin_${vphp}.so

EOF
fi

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
if [ -f "/usr/lib/systemd/system/php${php_version}-php-fpm.service" ];then 
  sed -i 's/PrivateTmp=true/PrivateTmp=false/' /usr/lib/systemd/system/php${php_version}-php-fpm.service 
  systemctl daemon-reload
  service php${php_version}-php-fpm start
else 
  mv /etc/init.d/php${php_version}-php-fpm /etc/init.d/php-fpm-${php_version}
  chmod +x /etc/init.d/php-fpm-${php_version}
  /etc/init.d/php-fpm-${php_version} start
fi
}

echo '=======================================================';
echo 'Your select to install:'
echo '=======================================================';
echo '1) PHP-5.4';
echo '2) PHP-5.5';
echo '3) PHP-5.6';
echo "4) PHP-7.0";
echo "5) PHP-7.1";
echo "6) PHP-7.2";
echo "7) PHP-7.3";
echo "8) PHP-7.4";
echo "9) PHP-8.0";
echo "10) PHP-8.1";
echo "11) PHP-8.2";
read -p "Plese select to add php version(1-11): " php;
echo '=======================================================';

case "${php}" in
  '1')
    vphp='5.4'
    php_version='54'
    ;;
  '2')
    vphp='5.5'
    php_version='55'
    ;;
  '3')
    vphp='5.6'
    php_version='56'
    ;;
  '4')
    vphp='7.0'
    php_version='70'
    ;;
  '5')
    vphp='7.1'
    php_version='71'
    ;;
  '6')
    vphp='7.2'
    php_version='72'
    ;;
  '7')
    vphp='7.3'
    php_version='73'
    ;;
  '8')
    vphp='7.4'
    php_version='74'
    ;;
  '9')
    vphp='8.0'
    php_version='80'
    ;;
  '10')
    vphp='8.1'
    php_version='81'
    ;;
  '11')
    vphp='8.2'
    php_version='82'
    ;;
esac

while [ "$go" != 'y' ] && [ "$go" != 'n' ]
  do
    read -p "Ready You a start the PHP-$vphp installation?(y/n): " go;
done
if [ "${go}" == 'n' ];then
  echo 'Your alrea cancel the install.';
  exit 1;
fi
Install_PHP
echo '=======================================================';
echo "php-$vphp successful"
