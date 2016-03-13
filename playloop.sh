#! /bin/sh

cd /home/music/LedDisplay

export LED_DEVICE=/dev/ttyUSB0

while true ; do
    echo "restart" >> metadata.log
    ./PlayInternetRadio.py
    sleep 5
done
