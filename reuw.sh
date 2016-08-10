#!/bin/bash
uwkode=`ps -ef | grep uwsgi-config.ini | awk -F ' ' '{print $2}' | sed -n 1p`
echo "Let's kill uwsgi $uwkode"
kill -9 $uwkode
echo "Start uwsgi"
sleep 2
/home/www/SEOS/venv/bin/uwsgi -d --ini /home/www/SEOS/uwsgi-config.ini --daemonize /var/log/uwsgi.log
echo `ps -ef | grep uwsgi-config.ini | awk -F ' ' '{print $2}' | sed -n 1p`
