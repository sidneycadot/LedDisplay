# Python module for the AM03127 (a.k.a. AM004-03127) LED display module.

# The device has 16 elements of 7 rows x 5 columns == 7 rows x 80 columns

import serial, operator, datetime

class CommunicationError(Exception):
    """This exception is raised if a communication error is detected."""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class LedDisplay(object):

    DEFAULT_RETRY = 3

    @staticmethod
    def __checkDeviceId(deviceId):
        if isinstance(deviceId, int) and (1 <= deviceId <= 8):
            return deviceId
        raise ValueError("%s is not a valid device ID." % deviceId)

    @staticmethod
    def __checkSchedule(schedule):
        if isinstance(schedule, str) and (len(schedule) == 1) and ("A" <= schedule <= "E"):
            return schedule
        raise ValueError("%s is not a valid schedule." % schedule)

    @staticmethod
    def __checkPage(page):
        if isinstance(page, str) and (len(page) == 1) and ("A" <= page <= "E"):
            return page
        raise ValueError("%s is not a valid page." % page)

    @staticmethod
    def __checkSchedulePages(schedulePages):
        if isinstance(schedulePages, str) and (len(schedulePages) <= 31):
            for page in schedulePages:
                LedDisplay.__checkPage(page)
            return schedulePages
        raise ValueError("%s is not a valid page schedule." % schedulePages)

    @staticmethod
    def __checkLine(line):
        if isinstance(line, int) and (1 <= line <= 8):
            return line
        raise ValueError("%s is not a valid line." % line)

    @staticmethod
    def __checkBrightness(brightness):
        if isinstance(brightness, str) and (len(brightness) == 1) and ("A" <= brightness <= "D"):
            return brightness
        raise ValueError

    @staticmethod
    def __checkGraphicsPage(graphicsPage):
        if isinstance(graphicsPage, str) and (len(graphicsPage) == 1) and ("A" <= graphicsPage <= "P"):
            return graphicsPage
        raise ValueError("%s is not a valid graphicsPage." % graphicsPage)

    @staticmethod
    def __checkGraphicsBlock(graphicsBlock):
        if isinstance(graphicsBlock, int) and (1 <= graphicsBlock <= 8):
            return graphicsBlock
        raise ValueError("%s is not a valid graphics block." % graphicsBlock)

    def __init__(self, device, device_id = 1, timeout = 1.0, noisy = False):

        self._device    = device
        self._device_id = self.__checkDeviceId(device_id)
        self._timeout   = timeout
        self._noisy     = noisy
        self._port      = serial.Serial(self._device, 9600, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, self._timeout, False, False)

        if self._noisy:
            print "[%s] opened port." % self._device

    def __del__(self):

        if self._port is not None:
            print "WARNING: __del__ method of class LedDisplay closes port. Please use explicit close() method!"
            self.close()

    def close(self):
        assert self._port is not None
        self._port.close()
        self._port = None
        if self._noisy:
            print "[%s] closed port." % self._device

    def send(self, data_packet, max_retry = DEFAULT_RETRY):
        """Assemble standard packet and send command."""
        checksum = reduce(operator.__xor__, map(ord, data_packet), 0)

        command = "<ID%02X>%s%02X<E>" % (self._device_id, data_packet, checksum)

        # Try up to "max_retry" times...

        for i in xrange(max_retry):
            if self._noisy:
                print "[%s] sending to device: \"%s\"" % (self._device, command)
            self._port.write(command)
            response = self._port.read(3)
            if response == "ACK":
                if self._noisy:
                    print "[%s] received acknowledgement." % self._device
                return # Success!
            response = response + self._port.read(1000) # will timeout
            if self._noisy:
                print "[%s] WARNING, no ACK received, got \"%s\" instead. Going for retry." % (self._device, response)

        # If we get back here, we didn't get an ACK.
        raise CommunicationError("Command \"%s\" was not acknowledged." % command)

    def setDeviceId(self, new_device_id, max_retry = DEFAULT_RETRY):
        """Paragraph 4.1: ID setting.
           Note that we cannot use the standard send() routine here. The "set ID" command
           is special because it lacks an ID number and a checksum."""

        command = "<ID><%02X><E>" % new_device_id

        # Try up to "max_retry" times...

        for i in xrange(max_retry):
            if self._noisy:
                print "[%s] sending to device: \"%s\"" % (self._device, command)
            self._port.write(command)
            response = self._port.read(2)
            if response == ("%02X" % new_device_id):
                if self._noisy:
                    print "[%s] received acknowledgement." % self._device
                return # Success!
            response = response + self._port.read(1000) # will timeout
            if self._noisy:
                print "[%s] WARNING, no acknowledge received, got \"%s\" instead. Going for retry." % (self._device, response)

        # If we get back here, we didn't get an acknowledgement.
        raise CommunicationError("Command \"%s\" was not acknowledged." % command)

    def setRealtimeClock(self, timestamp = None):
        """ Paragraph 4.2.1: Real Time Clock Setting"""
        if timestamp is None:
            timestamp = datetime.now()
        else:
            assert isinstance(timestamp, datetime.datetime)

        command = "<SC>%02d%02d%02d%02d%02d%02d%02d" % (
            timestamp.year % 100,
            timestamp.isoweekday(),
            timestamp.month,
            timestamp.day,
            timestamp.hour,
            timestamp.minute,
            timestamp.second
        )

        self.send(command)

    def setPageContent(self, content):
        """ Paragraph 4.2.2: Sending Page content"""
        assert False # TODO: implement and test

    def setSchedule(self, schedule, pages, startTime = None, stopTime = None):
        """ Paragraph 4.2.3: Sending Schedule"""

        if startTime is None:
            startTime = datetime.datetime(2000, 1, 1, 0, 0, 0)
        else:
            assert isinstance(startTime, datetime.datetime)

        if stopTime is None:
            stopTime = datetime.datetime(2099, 12, 31, 23, 59, 59)
        else:
            assert isinstance(stopTime, datetime.datetime)

        command = "<T%s>%02d%02d%02d%02d%02d%02d%02d%02d%02d%02d%s" % (
            self.__checkSchedule(schedule),
            startTime.year % 100,
            startTime.month,
            startTime.day,
            startTime.hour,
            startTime.minute,
            stopTime.year % 100,
            stopTime.month,
            stopTime.day,
            stopTime.hour,
            stopTime.minute,
            self.__checkSchedulePages(pages)
        )
        self.send(command)

    def setGraphicsBlock(self, graphicsPage, graphicsBlock, graphics):
        """ Paragraph 4.2.4: Send Graphic Block"""

        # A single Graphics block is 7 rows x 32 columns worth of pixels.
        # Each pixel can take any of four values, so it takes two bits to specidy a single pixel:
        #
        #   00 -> black
        #   01 -> green
        #   10 -> red
        #   11 -> orange
        #
        # E.g., to specify 4 horizontal pixels with colors RED, BLACK, ORANGE, RED translates to
        # binary 10001110, or a byte with value 0x8e.

        # A graphics block is actually specified as an 8-rows x 32 columns image; the last row is not used.
        # This is the order of the bytes used. Each byte specifies 4 adjacent pixels, as explained above.

        #  0   1  16  17  32  33  48  49
        #  2   3  18  19  34  35  50  51
        #  4   5  20  21  36  37  52  53
        #  6   7  22  23  38  39  54  55
        #  8   9  24  25  40  41  56  57
        # 10  11  26  27  42  43  58  59
        # 12  13  28  29  44  45  60  61
        # 14  15  30  31  46  47  62  63 --> pixels of this row (row 8) are not used.
        #
        # We expect the graphics specified in a string of length 7x32, consisting of the letters "G", "B", "O", "R".

        gr = []
        for i in xrange(64):
            px = (i % 2) + (i // 16) * 2
            # 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1
            # 2 3 2 3 2 3 2 3 2 3 2 3 2 3 2 3
            # 4 5 4 5 4 5 4 5 4 5 4 5 4 5 4 5
            # 6 7 6 7 6 7 6 7 6 7 6 7 6 7 6 7
            py = (i // 2) % 8
            # 0 0 1 1 2 2 3 3 4 4 5 5 6 6 7 7
            # 0 0 1 1 2 2 3 3 4 4 5 5 6 6 7 7
            # 0 0 1 1 2 2 3 3 4 4 5 5 6 6 7 7
            # 0 0 1 1 2 2 3 3 4 4 5 5 6 6 7 7

            if py == 7:
                pixels = "BBBB"
            else:
                pixels = graphics[py * 32 + 4 * px:py * 32 + 4 * px + 4]

            v = 0
            for p in pixels:
                v *= 4
                if   p == "G": v += 1
                elif p == "R": v += 2
                elif p == "O": v += 3

            gr.append(v)

        print "@@@@@@@@@@@", gr
        gr = "".join(["%c" % g for g in gr])

        command = "<G%s%d>%s" % (self.__checkGraphicsPage(graphicsPage), self.__checkGraphicsBlock(graphicsBlock), gr)
        self.send(command)

    def deletePage(self, line, page):
        """Paragraph 4.2.5.1: Delete page"""
        command = "<DL%sP%s>" % (self.__checkLine(line), self.__checkPage(page))
        self.send(command)

    def deleteSchedule(self, schedule):
        """Paragraph 4.2.5.2: Delete schedule"""
        command = "<DT%s>" % self.__checkSchedule(schedule)
        self.send(command)

    def deleteAll(self):
        """Paragraph 4.2.5.3: Delete all"""
        command = "<D*>"
        self.send(command)

    def setDefaultRunPage(self, page):
        """Paragraph 4.2.6: Assign a default run page"""
        command = "<RP%s>" % self.__checkPage(page)
        self.send(command)

    def setBrightnessLevel(self, brightness):
        """Paragraph 4.2.7: Assign Display Brightness level"""
        command = "<B%s>" % self.__checkBrightness(brightness)
        self.send(command)

    def changeFactoryDefaultEuropeanCharacterTable(self):
        """Paragraph 4.2.8: Change factory default European char table"""
        assert False # TODO: implement and test

    def setFactoryDefault(self):
        """Paragraph 4.2.9: Recall factory default European char table"""
        command = "<DU>"
        self.send(command)
