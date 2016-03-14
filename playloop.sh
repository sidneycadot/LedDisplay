#! /bin/sh

cd /home/music/LedDisplay

export LED_DEVICE=/dev/ttyUSB0

while true ; do
    ./PlayInternetRadio.py
    sleep 5
done
