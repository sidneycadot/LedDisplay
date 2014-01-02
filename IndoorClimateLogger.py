#! /usr/bin/env python

import sys
from LedDisplay import LedDisplay

def update_loop(ledz):

    last_command = ""

    rv_arr   = []
    temp_arr = []

    while True:
        line = raw_input()
        print ">>", line
        (timestamp, rv, temp) = line.split()

        rv = float(rv)
        temp = float(temp)

        rv_arr.append(rv)
        temp_arr.append(temp)

        rv_arr = rv_arr[-10:]
        temp_arr = temp_arr[-10:]

        rv   = sum(rv_arr) / len(rv_arr)
        temp = sum(temp_arr) / len(temp_arr)

        print rv_arr, temp_arr, rv, temp

        command = "<L1><PB><FP><MA><WC><FK><AC><CD>%5.1f %% %5.1f <U3A>C" % (rv, temp)

        if command != last_command:
            ledz.send(command)
            last_command = command

def main():

    device = "/dev/ttyUSB5"

    for arg in sys.argv[1:]:
        if arg.startswith("--device="):
            device = arg[9:]

    ledz = LedDisplay(device, noisy = True)

    ledz.setBrightnessLevel("A")
    ledz.setRealtimeClock()
    ledz.setSchedule("A", "AB")
    ledz.send("<L1><PA><FP><MA><WC><FK><AC><CD> <KD> <KT>")

    update_loop(ledz)

    ledz.close()

if __name__ == "__main__":
    main()
