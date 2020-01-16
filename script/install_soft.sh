#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
export LANG=en_US.UTF-8
export LANGUAGE=en_US:en

serverUrl=https://basoro.id/downloads/slemp

public_file=/opt/slemp/server/panel/script/public.sh
if [ ! -f $public_file ];then
	wget -O $public_file $serverUrl/public.sh -T 5;
fi
. $public_file

mtype=$1
actionType=$2
name=$3
version=$4

if [ ! -f 'lib.sh' ];then
	wget -O lib.sh $serverUrl/lib.sh
fi
wget -O $name.sh $serverUrl/$name.sh
if [ "$actionType" == 'install' ];then
	sh lib.sh
	rm -f lib.sh
fi
sh $name.sh $actionType $version
rm -f $name.sh
rm -f $public_file
