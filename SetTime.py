#! /usr/bin/env python3

import logging
import sys
from setup_logging import setup_logging
from LedDisplay import LedDisplay

def main():

    if "--debug" in sys.argv[1:]:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    log_format = "%(asctime)s | %(levelname)-10s | %(name)-25s | %(message)s"

    with setup_logging(logfile_name = None, fmt = log_format, level = log_level):

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
