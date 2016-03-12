#! /usr/bin/env python3

import time
import socket
import subprocess
import re
from LedDisplay import LedDisplay
import logging

logger = logging.getLogger(__name__)

class MP3Player:
    def __init__(self):
        self.process = subprocess.Popen(args = ["mpg123", "-"], stdin = subprocess.PIPE, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
        self.start_time = None
        self.bytecount = 0
        self.logger = logging.getLogger("MP3Player")
    def __del__(self):
        self.process.stdin.close()
        self.process.wait()
    def play(self, data):

        current_time = time.time()

        self.process.stdin.write(data)

        if self.start_time is None:
            self.start_time = current_time
    
        old_bytecount = self.bytecount
        self.bytecount += len(data)

        REPORT_INTERVAL = 1048576

        if (self.bytecount // REPORT_INTERVAL) > (old_bytecount // REPORT_INTERVAL):

            megabytes = self.bytecount / 1048576.0
            kilobits  = self.bytecount * 8.0 / 1000.0 # These 'kilobits' are 1000 bits.

            seconds = current_time - self.start_time
            hours = seconds / 3600.0

            megabytes_per_hour  = megabytes / hours
            kilobits_per_second = kilobits / seconds

            self.logger.info("Streamed {:.1f} MB in {:.3f} hours ({:.3f} MB/h, {:.3f} kbits/sec)".format(megabytes, hours, megabytes_per_hour, kilobits_per_second))

class MetadataProcessor:

    def __init__(self, device):
        self.regexp = re.compile("StreamTitle='(.*)';StreamUrl='(.*)';")
        self.led_display = LedDisplay(device)
        self.led_display.setBrightnessLevel("A")
        self.led_display.setSchedule("A", "A")

        self.logger = logging.getLogger("Metadata")

    def __del__(self):

        self.led_display.close()

    def process(self, metadata):

        match = self.regexp.match(metadata)

        title = match.group(1)
        title = title.rstrip()
        title = title.replace('  ', ' ')

        self.logger.info("Stream title: {!r}".format(title))

        message = "<L1><PA><FE><MA><WB><FE><AC><CD>{}          <CG><KD> <KT>".format(title)

        self.led_display.send(message)

class InternetRadioPlayer:

    def __init__(self, host, port, mp3player, metadata_processor):

        self.host = host
        self.port = port
        self.mp3player = mp3player
        self.metadata_processor = metadata_processor

        self.logger = logging.getLogger("InternetRadioPlayer")

    def play(self):

        MAX_PACKET_SIZE = 2048 # bigger than 1 packet.

        address = (self.host, self.port)

        stream_socket = socket.create_connection(address)

        try:
        
            request = "GET / HTTP/1.0\r\nHost:{}\r\nIcy-MetaData: 1\r\nAccept: */*\r\n\r\n".format(self.host).encode()

            self.logger.info("Sending HTTP request: {!r} to {}:{}".format(request, self.host, self.port))

            stream_socket.send(request)

            # Read the response header (HTTP-like).

            self.logger.debug("Parsing HTTP response.")

            stream_buffer = bytearray()
            icy_metadata_interval = None


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

                self.logger.info("Header line: {!r}".format(headerline))

                if headerline.startswith("icy-metaint:"):
                    icy_metadata_interval = int(headerline[12:])

                if len(headerline) == 0:
                    # Empty line terminates the header!
                    break

            assert icy_metadata_interval is not None
            
            # Stream MP3 data, interleaved with ICY metadata

            self.logger.debug("Interpret interleaved audio / ICY data.")

            while True:

                self.logger.debug("Read audio stream ({} bytes) ...".format(icy_metadata_interval))

                stream_mp3_bytes_until_metadata = icy_metadata_interval

                while stream_mp3_bytes_until_metadata > 0:

                    if len(stream_buffer) > 0:

                        stream_mp3_bytes = min(stream_mp3_bytes_until_metadata, len(stream_buffer))

                        if self.mp3player is not None:
                            self.mp3player.play(stream_buffer[:stream_mp3_bytes])

                        del stream_buffer[:stream_mp3_bytes]
                        stream_mp3_bytes_until_metadata -= stream_mp3_bytes

                    else:

                        packet = stream_socket.recv(MAX_PACKET_SIZE)
                        stream_buffer.extend(packet)

                # Read ICY metadata

                self.logger.debug("Read ICY metadata ...")

                while True:

                    if len(stream_buffer) >= 1:

                        metadata_size = 16 * stream_buffer[0]

                        if len(stream_buffer) >= 1 + metadata_size:

                            # We have a complete metadata chunk.
                            
                            # Process metadata, if a processor is defined
                            if self.metadata_processor is not None:
                                metadata = stream_buffer[1:1 + metadata_size]

                                if len(metadata) > 0:
                                    metadata = metadata.rstrip(b"\0")
                                    try:
                                        metadata = metadata.decode()
                                    except:
                                        self.logger.error("metadata decode error: {!r}".format(metadata))
                                        metadata = None

                                    if metadata is not None:
                                        self.metadata_processor.process(metadata)

                            # Discard the metadata chunk, and leave metadata parsing loop.
                                    
                            del stream_buffer[:1 + metadata_size]
                            break

                    # We need to read more metadata.

                    packet = stream_socket.recv(MAX_PACKET_SIZE)
                    stream_buffer.extend(packet)

        finally:

            stream_socket.close()

def main():

    logging_format = "%(asctime)s | %(levelname)-10s | %(name)-20s | %(message)s"
    logging.basicConfig(level = logging.INFO, format = logging_format)

    try:

        mp3player = MP3Player()
        metadata_processor = MetadataProcessor("/dev/ttyUSB0")

        #host = "as192.pinguinradio.com"
        #host = "pu192.pinguinradio.com"
        host = "pc192.pinguinradio.com"

        port = 80

        player = InternetRadioPlayer(host, port, mp3player, metadata_processor)
        player.play()

    finally:

        logging.shutdown()

if __name__ == "__main__":
    main()

