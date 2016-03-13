#! /bin/sh

cd /home/music/LedDisplay

export LED_DISPLAY=/dev/ttyUSB0

while true ; do
    echo "restart" >> metadata.log
    ./PlayInternetRadio.py
    sleep 5
done
