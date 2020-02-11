#!/bin/bash
set -e


env >> /etc/default/locale
/etc/init.d/cron start
service nginx start
python3 ./main.py &
exec "$@"