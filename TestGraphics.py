#! /usr/bin/env python3

from LedDisplay import LedDisplay
import random
from setup_logging import setup_logging

with setup_logging():

    with LedDisplay("/dev/ttyUSB0") as led_display:

        # Define display schedule.
        led_display.setSchedule("A", "A")

        gr1 = [
            "RRRRRRRGGGGGGGGGGGGGGGGGGGGGGGGO",
            "RRRRRRGGGGGGGGGGGGGGGGGGGGGGGGOO",
            "RRRRRGGGGGGGGGGGGGGGGGGGGGGGGOOO",
            "RRRRGGGGGGGGGGGGGGGGGGGGGGGGOOOO",
            "RRRGGGGGGGGGGGGGGGGGGGGGGGGOOOOO",
            "RRGGGGGGGGGGGGGGGGGGGGGGGGOOOOOO",
            "RGGGGGGGGGGGGGGGGGGGGGGGGOOOOOOO"
        ]

        gr2 = [
            "RRRGGGGGGGGGGGGGGGGGGGGGGGGGGRRR",
            "RGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGR",
            "RGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGR",
            "RGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGR",
            "RGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGR",
            "RGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGR",
            "RRRGGGGGGGGGGGGGGGGGGGGGGGGGGRRR"
        ]

        gr3 = [
            "OOOOOOOOOOOOOOOO.OOOOOOOOOOOOOOO",
            "OOOOOOOOOOOOOOOO.OOOOOOOOOOOOOOO",
            "OOOOOOOOOOOOOOOO.OOOOOOOOOOOOOOO",
            "OOOOOOOOOOOOOOOR.OOOOOOOOOOOOOOO",
            "OOOOOOOOOOOOOOOO.OOOOOOOOOOOOOOO",
            "OOOOOOOOOOOOOOOO.OOOOOOOOOOOOOOO",
            "OOOOOOOOOOOOOOOO.OOOOOOOOOOOOOOO"
        ]

        gr1= "".join(gr1)
        gr2= "".join(gr2)
        gr3= "".join(gr3)

        led_display.setGraphicsBlock("A", 1, gr1)
        led_display.setGraphicsBlock("A", 2, gr2)
        led_display.setGraphicsBlock("A", 3, gr3)

        led_message = "<L1><PA><FA><MA><WA><FK><CB>L1/PA<U0F><GA1><U0F>"
        led_display.send(led_message)
        led_message = "<L1><PB><FA><MA><WA><FK><GA1><GA2><GA3>"
        led_display.send(led_message)
        led_message = "<L1><PC><FA><MA><WA><FK><CH>L1/PC<U0F><GA3><U0F>"
        led_display.send(led_message)



        #led_display.send(b"<GA1>" + 200 * b"C")
