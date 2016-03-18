#! /usr/bin/env python3

import os, select, sys, time, socket, re, subprocess, logging, math, sqlite3
from setup_logging import setup_logging

try:
    from LedDisplay import LedDisplay
except:
    pass # Error while importing

class Signal:
    """ A lightweight implementation of the Signal/Slot mechanism.
    """
    def __init__(self):
        self._receivers = []
        self._logger = logging.getLogger("signal")
    def connect(self, receiver):
        self._receivers.append(receiver)
    def emit(self, *args, **kwargs):
        # Note: if any of the receivers raises a signal,
        # the other receivers will not be notified.
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
            self._logger.error("The __del__ method of class AudioStreamPlayer was called while the subprocess was still active. Please use explicit close() method.")
            self.close()

    def __enter__(self):

        return self

    def __exit__(self, exc_type, exc_value, traceback):

        if self._process is not None:
            self.close()

    def close(self):

        assert self._process is not None

        self._logger.debug("Stopping {!r} sub-process.".format(self._executable))
        self._process.terminate() # ask nicely
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
        # No-op
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

            # The "reggae" easter egg...

            check_title = title.lower()

            if ("bob marley" in check_title) or ("peter tosh" in check_title) or ("reggae" in check_title):
                color_directive = "<CR>"
            else:
                color_directive = "<CD>"

            # Make led display command.

            led_message = "<L1><PA><FE><MA><WB><FE><AC>{}{}          <CG><KD> <KT>".format(color_directive, title)

            with LedDisplay(self._led_device) as led_display:
                led_display.send(led_message)

class MetadataFileWriter:

    def __init__(self, filename):

        self._logger = logging.getLogger("MetadataFileWriter")

        self._filename = filename

        with open(self._filename, "a", encoding = "utf-8") as f:
            print("restart", file = f)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def process(self, current_time, metadata):

        if len(metadata) == 0:
            return

        with open(self._filename, "a", encoding = "utf-8") as f:
            print("{:20.9f} {}".format(current_time, metadata), file = f)

class MetadataDatabaseWriter:

    def __init__(self, filename):

        self._logger = logging.getLogger("MetadataDatabaseWriter")

        self._logger.debug("Opening database ...")
        self._conn = sqlite3.connect(filename)

        cursor = self._conn.cursor()

        query = """CREATE TABLE IF NOT EXISTS metadata(
                    id         INTEGER NOT NULL PRIMARY KEY,
                    timestamp  REAL    NOT NULL,
                    duration   REAL        NULL,
                    metadata   BLOB    NOT NULL
                );"""

        query = query.split("\n")
        query[1:] = [q[16:] for q in query[1:]]
        query = "\n".join(query)

        cursor.execute(query)

        self._counter = 0
        self._last_time  = None
        self._last_rowid = None

    def __del__(self):
        if self._conn is not None:
            self._logger.error("The __del__ method of class MetadataDatabaseWriter was called while the writer was still active. Please use explicit close() method.")
            self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._conn is not None:
            self.close()

    def close(self):
        assert self._conn is not None
        self._logger.debug("Closing database ...")
        self._conn.close()
        self._conn = None

    def process(self, current_time, metadata):

        if len(metadata) == 0:
            return

        self._counter += 1

        cursor = self._conn.cursor()

        # The duration of the first song cannot be determined.
        # The duration of the second song cannot be reliably calculated
        #    (because the timestamp of the first song is unreliable).

        if self._counter > 2:
            duration = current_time - self._last_time
            query = "UPDATE metadata SET duration = ? WHERE rowid = ?;"
            cursor.execute(query, (duration, self._last_rowid))

        query = "INSERT INTO metadata(timestamp, metadata) VALUES (?, ?);"

        cursor.execute(query, (current_time, metadata))

        self._conn.commit()

        self._last_time  = current_time
        self._last_rowid = cursor.lastrowid

class StreamStalledError(RuntimeError):
    pass

class InternetRadioPlayer:

    def __init__(self, host, port, path):

        self._logger = logging.getLogger("{}:{}".format(host, port))

        self._host = host
        self._port = port
        self._path = path

        self.audiodata_signal = Signal()
        self.metadata_signal = Signal()

    def play(self):

        SOCKET_RECV_TIMEOUT    =  1.0 # seconds
        SOCKET_RECV_SIZE       = 4096 # larger than 1 regular IP packet.
        NO_DATA_THRESHOLD_TIME = 10.0

        address = (self._host, self._port)

        stream_socket = socket.create_connection(address)

        try:

            request = "GET {} HTTP/1.0\r\nHost:{}\r\nIcy-MetaData: 1\r\nAccept: */*\r\n\r\n".format(self._path, self._host).encode()

            self._logger.info("Sending HTTP request: {!r} ...".format(request))

            stream_socket.send(request)

            # Read the response header (HTTP-like).

            stream_buffer = bytearray()
            last_data_time = time.time()

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

                        if len(stream_buffer) == 0:
                            break # We need more data -- at least the metadata chunk length byte.

                        metadata_size = 16 * stream_buffer[0]

                        if len(stream_buffer) < 1 + metadata_size:
                            break # We need more data; metadata chunk incomplete.

                        # We have a complete metadata chunk.
                        metadata = stream_buffer[1:1 + metadata_size]

                        metadata = metadata.rstrip(b"\0").decode(errors = "replace")

                        self.metadata_signal.emit(last_data_time, metadata)

                        # Discard the metadata size byte as well as the metadata itself.
                        del stream_buffer[:1 + metadata_size]

                        # Next traversal of data process loop will need to emit audio data
                        stream_audio_bytes_until_metadata = icy_metadata_interval

                # Read more data.

                while True:
                    (rlist, wlist, xlist) = select.select([stream_socket], [], [stream_socket], SOCKET_RECV_TIMEOUT)
                    select_time = time.time()
                    assert len(wlist) == 0
                    assert len(xlist) == 0
                    if stream_socket in rlist:
                        break # data available
                    self._logger.warning("No data received for {:.1f} seconds.".format(select_time - last_data_time))
                    if select_time - last_data_time > NO_DATA_THRESHOLD_TIME:
                        raise StreamStalledError()

                last_data_time = select_time
                packet = stream_socket.recv(SOCKET_RECV_SIZE)
                stream_buffer.extend(packet)

        finally:

            stream_socket.close()

def main():

    host = "pc192.pinguinradio.com"
    port = 80
    path = "/"

    led_device = os.getenv("LED_DEVICE")

    if "--debug" in sys.argv[1:]:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    log_filename = "PlayInternetRadio_%Y%m%d_%H%M%S.log"
    log_format = "%(asctime)s | %(levelname)-10s | %(name)-25s | %(message)s"

    with setup_logging(logfile_name = log_filename, fmt = log_format, level = log_level):

        logger = logging.getLogger("main")

        with AudioStreamPlayer("mpg123", ["-"]) as audiostream_player, \
             MetadataLedDisplayDriver(led_device) as metadata_led_driver, \
             MetadataDatabaseWriter("metadata.sqlite3") as metadata_database_writer, \
             MetadataFileWriter("metadata.log") as metadata_file_writer:

            radioPlayer = InternetRadioPlayer(host, port, path)

            radioPlayer.audiodata_signal.connect(audiostream_player.play)
            radioPlayer.metadata_signal.connect(metadata_led_driver.process)
            radioPlayer.metadata_signal.connect(metadata_file_writer.process)
            radioPlayer.metadata_signal.connect(metadata_database_writer.process)

            try:
                radioPlayer.play() # blocking call
            except KeyboardInterrupt:
                logger.info("Quitting due to user request.")
            except StreamStalledError:
                logger.info("Stream has stalled; quitting.")
            except BaseException as exception:
                logger.exception("Unknown exception while playing: {!r}".format(exception))

if __name__ == "__main__":
    main()
