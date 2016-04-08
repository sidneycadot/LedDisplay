#! /usr/bin/env python3

import sys
from LedDisplay import LedDisplay

def main():

    device = "/dev/ttyUSB0"

    for arg in sys.argv[1:]:
        if arg.startswith("--device="):
            device = arg[9:]

    ledz = LedDisplay(device)

    ledz.setBrightnessLevel("A")
    ledz.setRealtimeClock()
    ledz.setSchedule("A", "A")
    ledz.send("<L1><PA><FA><MA><WZ><FA><AC><CD> <KD> <KT>")

    ledz.close()

if __name__ == "__main__":
    main()

