#! /usr/bin/env python3

import os, time, socket, re, subprocess, logging, math

from LedDisplay import LedDisplay

class Signal:
    """ A very lightweight implementation of the Signal/Slot mechanism.
    """
    def __init__(self):
        self._receivers = []
    def connect(self, receiver):
        self._receivers.append(receiver)
    def emit(self, *args, **kwargs):
        for receiver in self._receivers:
            receiver(*args, **kwargs)

class AudioStreamPlayer:
    """ A basic audioplayer class that pushes data to a subprocess audio player.
    """
    def __init__(self, executable, executable_options):

        self._logger = logging.getLogger(executable)

        self._executable = executable

        self._logger.debug("Starting {!r} sub-process ...".format(self._executable))

        args = [executable] + [option for option in executable_options]

        self._process = subprocess.Popen(args = args, stdin = subprocess.PIPE, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

        self._last_report_time = float("-inf")
        self._bytecount = 0
        self._start_time = time.time()

    def __del__(self):

        if self._process is not None:
            self._logger.error("The__del__ method of class AudioStreamPlayer was called while the subprocess was still active. Please use explicit close() method.")
            self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._process is not None:
            self.close()

    def close(self):

        assert self._process is not None

        self._logger.debug("Stopping {!r} sub-process.".format(self._executable))
        self._process.wait()
        self._process = None

    def play(self, data):

        current_time = time.time()

        self._process.stdin.write(data)

        self._bytecount += len(data)

        REPORT_INTERVAL_SECONDS = 30.0

        if current_time - self._last_report_time >= REPORT_INTERVAL_SECONDS:

            megabytes = self._bytecount / 1048576.0
            kilobits  = self._bytecount * 8.0 / 1000.0 # These 'kilobits' are 1000 bits.

            seconds = current_time - self._start_time
            hours = seconds / 3600.0

            megabytes_per_hour  = megabytes / hours
            kilobits_per_second = kilobits / seconds

            hms_s = seconds
            hms_h = math.floor(hms_s / 3600.0)
            hms_s -= hms_h * 3600.0
            hms_m = math.floor(hms_s / 60.0)
            hms_s -= hms_m * 60.0

            self._logger.info("Streamed {:.3f} MB in {}h{:02}m{:06.3f}s ({:.3f} MB/h, {:.6f} kbits/sec)".format(megabytes, hms_h, hms_m, hms_s, megabytes_per_hour, kilobits_per_second))

            self._last_report_time = current_time

class MetadataProcessor:

    def __init__(self, led_device):

        self.logger = logging.getLogger("metadata")

        self.led_device = led_device

        self.regexp = re.compile("StreamTitle='(.*)';StreamUrl='(.*)';")

        if led_device is not None:
            with LedDisplay(self.led_device) as led_display:
                led_display.setBrightnessLevel("A")
                led_display.setSchedule("A", "A")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def process(self, metadata):

        match = self.regexp.match(metadata)

        title = match.group(1)
        title = title.rstrip()
        title = title.replace('  ', ' ')

        self.logger.info("Stream title: {!r}".format(title))

        if self.led_device is not None:

            led_message = "<L1><PA><FE><MA><WB><FE><AC><CD>{}          <CG><KD> <KT>".format(title)

            with LedDisplay(self.led_device) as led_display:
                led_display.send(led_message)

class InternetRadioPlayer:

    def __init__(self, host, port):

        self.logger = logging.getLogger("{}:{}".format(host, port))

        self.host = host
        self.port = port

        self.audiodata_signal = Signal()
        self.metadata_signal = Signal()

    def play(self):

        MAX_PACKET_SIZE = 2048 # bigger than 1 packet.

        address = (self.host, self.port)

        stream_socket = socket.create_connection(address)

        try:

            request = "GET / HTTP/1.0\r\nHost:{}\r\nIcy-MetaData: 1\r\nAccept: */*\r\n\r\n".format(self.host).encode()

            self.logger.info("Sending HTTP request: {!r} ...".format(request))

            stream_socket.send(request)

            # Read the response header (HTTP-like).

            self.logger.debug("Parsing HTTP response.")

            stream_buffer = bytearray()
            icy_metadata_interval = None
            icy_content_type = None

            while True:

                idx = stream_buffer.find(b"\r\n")

                if idx < 0:
                    # Read more data.
                    packet = stream_socket.recv(MAX_PACKET_SIZE)
                    stream_buffer.extend(packet)
                    # Interpret header
                    continue

                # Extract header line from stream buffer and convert it to a string.
                headerline = stream_buffer[:idx].decode()

                # Discard header line and CR/LF from stream buffer.
                del stream_buffer[:idx + 2]

                self.logger.info("Received response header: {!r}".format(headerline))

                if headerline.startswith("icy-metaint:"):
                    assert icy_metadata_interval is None
                    icy_metadata_interval = int(headerline[12:])
                elif headerline.startswith("content-type:"):
                    assert icy_content_type is None
                    icy_content_type = headerline[13:]
                elif len(headerline) == 0:
                    # Empty line terminates the header!
                    break

            assert icy_metadata_interval is not None
            assert icy_content_type      is not None

            # Stream MP3 data, interleaved with ICY metadata

            self.logger.debug("Interpret interleaved audio / ICY data.")

            while True:

                self.logger.debug("Read audio stream ({} bytes) ...".format(icy_metadata_interval))

                stream_mp3_bytes_until_metadata = icy_metadata_interval

                while stream_mp3_bytes_until_metadata > 0:

                    if len(stream_buffer) > 0:

                        stream_mp3_bytes = min(stream_mp3_bytes_until_metadata, len(stream_buffer))

                        self.audiodata_signal.emit(stream_buffer[:stream_mp3_bytes])

                        del stream_buffer[:stream_mp3_bytes]
                        stream_mp3_bytes_until_metadata -= stream_mp3_bytes

                    else:

                        packet = stream_socket.recv(MAX_PACKET_SIZE)
                        stream_buffer.extend(packet)

                # Read ICY metadata

                self.logger.debug("Read ICY metadata ...")

                while True:

                    current_time = time.time()

                    if len(stream_buffer) >= 1:

                        metadata_size = 16 * stream_buffer[0]

                        if len(stream_buffer) >= 1 + metadata_size:

                            # We have a complete metadata chunk.

                            metadata = stream_buffer[1:1 + metadata_size]

                            if len(metadata) > 0:

                                metadata = bytes(metadata.rstrip(b"\0"))

                                with open("metadata.log", "a") as f:
                                    print("{:20.9f} {!r}".format(current_time, metadata), file = f)

                                try:
                                    metadata = metadata.decode()
                                except:
                                    self.logger.error("metadata decode error: {!r}".format(metadata))
                                    metadata = None

                                if metadata is not None:
                                    self.metadata_signal.emit(metadata)

                            # Discard the metadata chunk, and leave metadata parsing loop.

                            del stream_buffer[:1 + metadata_size]
                            break

                    # We need to read more metadata.

                    packet = stream_socket.recv(MAX_PACKET_SIZE)
                    stream_buffer.extend(packet)

        finally:

            stream_socket.close()

def main():

    logging_format = "%(asctime)s | %(levelname)-10s | %(name)-25s | %(message)s"
    logging.basicConfig(level = logging.INFO, format = logging_format)

    try:

        #host = "as192.pinguinradio.com"
        #host = "pu192.pinguinradio.com"
        host = "pc192.pinguinradio.com"
        #host = "pcaac.pinguinradio.com"

        port = 80

        radioPlayer = InternetRadioPlayer(host, port)

        led_device = os.getenv(LED_DEVICE)

        with AudioStreamPlayer("mpg123", ["-"]) as audiostream_player, \
             MetadataProcessor(led_device) as metadata_processor:

            radioPlayer.audiodata_signal.connect(audiostream_player.play)
            radioPlayer.metadata_signal.connect(metadata_processor.process)

            radioPlayer.play() # blocking call

    except KeyboardInterrupt:

        logging.info("Quitting due to user request.")

    finally:

        logging.shutdown()

if __name__ == "__main__":
    main()
