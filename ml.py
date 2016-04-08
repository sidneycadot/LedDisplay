#! /usr/bin/env python3

import sys
import numpy as np
import scipy.special
import scipy.optimize

def HarmonicNumber(s):
    return np.euler_gamma + scipy.special.digamma(s + 1)

def MaximumLikelihoodEstimator(us, ts):
    return scipy.optimize.brentq(lambda n : n * (HarmonicNumber(n) - HarmonicNumber(n - us)) - ts, us, ts * 100000)

if __name__ == "__main__":

    dd = [int(arg) for arg in sys.argv[1:]]

    us = np.sum(dd)
    ts = np.dot(dd, np.arange(1, len(dd) + 1))

    ml = MaximumLikelihoodEstimator(us, ts)

    print("dd: {} us: {} ts: {} best estimate: {}".format(dd, us, ts, ml))
