# -*- coding: utf-8 -*-

# AM03127 aka AM004-03127

#device has 16 elements of 8 rows x 5 columns == 8 rows x 80 columns

import serial, operator, datetime

class CommunicationError(Exception):
    """This exception is raised if a communication error is detected."""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class LedDisplay(object):

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

    def send_raw(self, command, max_retry = 3):
        """This handles commands that have a checksum and commands that don't."""

        # Try up to three times...
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
        raise CommunicationError("Unable to send command \"%s\"" % command)

    def send(self, data_packet, max_retry = 3):
        """Assemble standard packet and send command."""
        checksum = reduce(operator.__xor__, map(ord, data_packet), 0)

        command = "<ID%02X>%s%02X<E>" % (self._device_id, data_packet, checksum)

        return self.send_raw(command, max_retry)

    def setDeviceId(self, new_device_id):
        """Paragraph 4.1: ID setting"""
        assert False # TODO: implement and test
        assert isinstance(new_device_id, int)
        assert 0 <= new_device_id <= 255
        # Note: this is a non-standard command, without an ID and checksum. Send using send_raw().
        command = "<ID>%02X<E>" % self.__checkDeviceId(new_device_id)
        self.send_raw(command)
        # If this succeeded, the device ID must be updated.
        self._device_id = new_device_id

    def setRealtimeClock(self, timestamp = None):
        """ Paragraph 4.2.1: Real Time Clock Setting"""
        if timestamp is None:
            timestamp = datetime.datetime.now()
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
            startTime = datetime.datetime(2000, 1, 1)
        else:
            assert isinstance(startTime, datetime.datetime)

        if stopTime is None:
            stopTime = datetime.datetime(2099, 12, 31)
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

    def setGraphicsBlock(self, block):
        """ Paragraph 4.2.4: Send Graphic Block"""
        assert False # TODO: implement and test

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
