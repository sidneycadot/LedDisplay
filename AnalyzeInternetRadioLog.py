#! /usr/bin/env python3

import re

with open("metadata.log") as f:
    lines = f.readlines()

metadata_regexp = re.compile("StreamTitle='(.*)  - (.*) ';StreamUrl='(.*)';")

prevartist     = None
prevsongtitle  = None
prevtimestamp  = None

trust_timestamp = False

for line in lines:
    line = line.rstrip()

    if line == "restart":
        if prevsongtitle is not None:
            print("{:12.6f} | {:30} | {}".format(float("nan"), prevartist, prevsongtitle))
        trust_timestamp = None
        prevartist    = None
        prevsongtitle = None
        prevtimestamp = None
        continue

    if trust_timestamp:
        timestamp = float(line[:20])
    else:
        timestamp = float("nan")

    metadata  = eval(line[21:]).decode()

    if prevsongtitle is not None:
        print("{:12.6f} | {:30} | {}".format(timestamp - prevtimestamp, prevartist, prevsongtitle))

    match = metadata_regexp.match(metadata)
    assert match is not None
    artist     = match.group(1).strip()
    songtitle  = match.group(2).strip()
    stream_url = match.group(3)


    trust_timestamp = True
    prevartist      = artist
    prevsongtitle   = songtitle
    prevtimestamp   = timestamp

if prevsongtitle is not None:
    print("{:12.6f} | {:30} | {}".format(float("nan"), prevartist, prevsongtitle))
