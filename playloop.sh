#! /bin/sh

cd /home/music/LedDisplay

while true ; do
    echo "restart" >> metadata.log
    ./PlayInternetRadio.py
    sleep 5
done