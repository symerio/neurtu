# neurtu, BSD 3 clause license
# Authors: Roman Yurchak

# redefine a few statistical functions to avoid additional dependencies


def _mean(x):
    """Return the mean of a sequence"""
    if len(x) < 1:
        raise ValueError('mean requires at least one data point')
    return sum(x) / len(x)


def _ss(data):
    """Return sum of square deviations of a sequence."""
    c = _mean(data)
    ss = sum((x-c)**2 for x in data)
    return ss


def _stddev(data, ddof=0):
    """Calculate the population standard deviation
    """
    n = len(data)
    if n < 2:
        raise ValueError('variance requires at least two data points')
    ss = _ss(data)
    pvar = ss/n
    return pvar**0.5


try:
    import numpy as np
    mean = np.mean
    stddev = np.std
except ImportError:
    mean = _mean
    stddev = _stddev
