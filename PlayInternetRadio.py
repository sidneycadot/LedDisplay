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

class MetadataLedDisplayDriver:

    def __init__(self, led_device):

        self._logger = logging.getLogger("MetadataLedDisplayDriver")

        self._led_device = led_device

        self._regexp = re.compile("StreamTitle='(.*)';StreamUrl='(.*)';")

        if self._led_device is not None:
            with LedDisplay(self._led_device) as led_display:
                led_display.setBrightnessLevel("A")
                led_display.setSchedule("A", "A")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def process(self, current_time, metadata):

        if len(metadata) == 0:
            return

        match = self._regexp.match(metadata)

        title = match.group(1)
        title = title.rstrip()
        title = title.replace('  ', ' ')

        self._logger.info("Stream title: {!r}".format(title))

        if self._led_device is not None:

            led_message = "<L1><PA><FE><MA><WB><FE><AC><CD>{}          <CG><KD> <KT>".format(title)

            with LedDisplay(self._led_device) as led_display:
                led_display.send(led_message)

class MetadataFileWriter:

    def __init__(self, filename):

        self._logger = logging.getLogger("MetadataFileWriter")

        self._filename = filename

        with open(self._filename, "a") as f:
            print("restart", file = f)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def process(self, current_time, metadata):

        if len(metadata) == 0:
            return

        with open(self._filename, "a") as f:
            print("{:20.9f} {}".format(current_time, metadata), file = f)

class InternetRadioPlayer:

    def __init__(self, host, port, path):

        self._logger = logging.getLogger("{}:{}".format(host, port))

        self._host = host
        self._port = port
        self._path = path

        self.audiodata_signal = Signal()
        self.metadata_signal = Signal()

    def play(self):

        MAX_PACKET_SIZE = 2048 # larger than 1 regular IP packet.

        address = (self._host, self._port)

        stream_socket = socket.create_connection(address)

        try:

            request = "GET {} HTTP/1.0\r\nHost:{}\r\nIcy-MetaData: 1\r\nAccept: */*\r\n\r\n".format(self._path, self._host).encode()

            self._logger.info("Sending HTTP request: {!r} ...".format(request))

            stream_socket.send(request)

            # Read the response header (HTTP-like).

            stream_buffer = bytearray()

            in_header = True
            icy_metadata_interval = None
            icy_content_type = None

            while True: # Loop to read more data.

                while True: # loop to process available bytes.

                    if in_header:

                        idx = stream_buffer.find(b"\r\n")

                        if idx < 0:
                            break # CR/LF not found. We need to read more data to proceed.

                        # Found CR/LF ; extract and process the line.

                        # Extract header line from stream buffer and convert it to a string.
                        headerline = stream_buffer[:idx].decode()

                        # Discard header line and CR/LF characters from the stream buffer.
                        del stream_buffer[:idx + 2]

                        self._logger.info("Received response header: {!r}".format(headerline))

                        if headerline.startswith("icy-metaint:"):
                            assert icy_metadata_interval is None
                            icy_metadata_interval = int(headerline[12:])
                        elif headerline.startswith("content-type:"):
                            assert icy_content_type is None
                            icy_content_type = headerline[13:]
                        elif len(headerline) == 0:
                            # Empty line terminates the header!
                            assert icy_metadata_interval is not None
                            assert icy_content_type is not None
                            stream_audio_bytes_until_metadata = icy_metadata_interval
                            in_header = False
                    elif stream_audio_bytes_until_metadata > 0:

                        # We should stream audio data.
                        if len(stream_buffer) == 0:
                            break # No data available for streaming. Need to read more data.

                        # Determine how mouch of the buffer we should stream.
                        stream_audio_bytes = min(stream_audio_bytes_until_metadata, len(stream_buffer))

                        # Emit the data as audio.
                        self.audiodata_signal.emit(stream_buffer[:stream_audio_bytes])

                        # Remove the audio stream data from the stream buffer.
                        del stream_buffer[:stream_audio_bytes]

                        # Decrease the number of bytes until the next metadata chunk.
                        stream_audio_bytes_until_metadata -= stream_audio_bytes
                    else:
                        # We are expecting a metadata chunk.
                        current_time = time.time()

                        packet = stream_socket.recv(MAX_PACKET_SIZE)
                        stream_buffer.extend(packet)

                        if len(stream_buffer) == 0:
                            break # We need more data -- at least the metadata chunk length byte.

                        metadata_size = 16 * stream_buffer[0]

                        if len(stream_buffer) < 1 + metadata_size:
                            break # We need more data; metadata chunk incomplete.

                        # We have a complete metadata chunk.
                        metadata = stream_buffer[1:1 + metadata_size]

                        metadata = metadata.rstrip(b"\0").decode(errors = "replace")

                        self.metadata_signal.emit(current_time, metadata)

                        # Discard the metadata size byte as well as the metadata itself.
                        del stream_buffer[:1 + metadata_size]

                        # Next traversal of data process loop will need to emit audio data
                        stream_audio_bytes_until_metadata = icy_metadata_interval

                # Read more data.
                packet = stream_socket.recv(MAX_PACKET_SIZE)
                stream_buffer.extend(packet)

        #except BaseException as exception:
        #    self._logger.exception(exception)
        #    raise

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
        path = "/"

        radioPlayer = InternetRadioPlayer(host, port, path)

        led_device = os.getenv("LED_DEVICE")

        with AudioStreamPlayer("mpg123", ["-"]) as audiostream_player,    \
             MetadataLedDisplayDriver(led_device) as metadata_led_driver, \
             MetadataFileWriter("metadata.log") as metadata_file_writer:

            radioPlayer.audiodata_signal.connect(audiostream_player.play)
            radioPlayer.metadata_signal.connect(metadata_led_driver.process)
            radioPlayer.metadata_signal.connect(metadata_file_writer.process)

            radioPlayer.play() # blocking call

    except KeyboardInterrupt:

        logging.info("Quitting due to user request.")

    finally:

        logging.shutdown()

if __name__ == "__main__":
    main()
