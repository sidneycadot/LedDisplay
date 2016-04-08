#! /usr/bin/env python3

import re, sys, math, collections
import numpy as np
import scipy.optimize, scipy.special

def read_log(filename):

    with open("metadata.log", "r") as f:
        lines = f.readlines()

    metadata_regexp = re.compile("StreamTitle='(.*)  - (.*) ';StreamUrl='(.*)';")

    prevartist     = None
    prevsongtitle  = None
    prevtimestamp  = None

    # We cannot trust the first timestamp after a restart; the metadata is always emitted,
    # even if the song is halfway done.

    trust_next_timestamp = False

    songs = []

    for line in lines:

        line = line.rstrip()

        if line == "restart":

            if prevsongtitle is not None:
                song = (prevartist, prevsongtitle, float("nan"))
                songs.append(song)

            prevartist      = None
            prevsongtitle   = None
            prevtimestamp   = None

            trust_next_timestamp = False

            continue

        # An actual song line was found.
        # Parse its data.

        if trust_next_timestamp:
            timestamp = float(line[:20])
        else:
            timestamp = float("nan")

        metadata = line[21:]

        match = metadata_regexp.match(metadata)
        if match is None:
            print("Match failure: {!r} ; aborting.".format(metadata))
        assert match is not None

        artist     = match.group(1).strip()
        songtitle  = match.group(2).strip()
        stream_url = match.group(3)

        # Make a record of the previous song, now that we know its duration.

        if prevsongtitle is not None:
            song = (prevartist, prevsongtitle, timestamp - prevtimestamp)
            songs.append(song)

        # Prepare for next song.

        prevartist      = artist
        prevsongtitle   = songtitle
        prevtimestamp   = timestamp

        trust_next_timestamp = True

    # Done reading songs.
    # Handle the last song, if there is one. It has no known duration.

    if prevsongtitle is not None:
        song = (prevartist, prevsongtitle, float("nan"))
        songs.append(song)

    return songs

def print_songs(songs):
    for (artist, songtitle, duration) in songs:
        print("{:12.6f} | {:30} | {}".format(duration, artist, songtitle))

def HarmonicNumber(s):
    return np.euler_gamma + scipy.special.digamma(s + 1)

def MaximumLikelihoodEstimator(us, ts):
    return scipy.optimize.brentq(lambda n : n * (HarmonicNumber(n) - HarmonicNumber(n - us)) - ts, us, ts * 100000)

def analyze_maximum_likelihood(songs):

    # Filter songs
    songs = [(artist, songtitle, duration) for (artist, songtitle, duration) in songs if "PINGUIN" not in artist and not math.isnan(duration)]

    # Count artist / songtitle pairs
    counter = collections.Counter((artist, songtitle) for (artist, songtitle, duration) in songs)

    countercounter = collections.Counter(counter.values())

    maxcount = max(countercounter.keys())

    dd = [countercounter[count] for count in range(1, maxcount + 1)]

    us = np.sum(dd)
    ts = np.dot(dd, 1 + np.arange(len(dd)))
    ml = MaximumLikelihoodEstimator(us, ts)

    print("dd: {} us: {} ts: {} best estimate: {:.3f}".format(dd, us, ts, ml))

if __name__ == "__main__":
    filename = "metadata.log"
    songs = read_log(filename)

    if len(sys.argv) == 1:
        print_songs(songs)
    else:
        for arg in sys.argv[1:]:
            if arg == "--ml":
                analyze_maximum_likelihood(songs)
