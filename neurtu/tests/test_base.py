from __future__ import division

import sys
from time import sleep
import pytest
from pytest import approx

from neurtu import timeit, memit, delayed


def test_timeit_overhead():

    dt = 0.2

    res = timeit(delayed(sleep)(dt))

    # overhead should be less than 500 us

    if sys.platform == 'win32':
        # precision of time.time on windows is 16 ms
        timer_precision = 25e-3
    elif sys.platform == 'darwin':
        # for some reason on OS X time.sleep appears to be
        # quite inaccurate
        timer_precision = 80e-3
    else:
        timer_precision = 5e-3

    assert res['wall_time_mean'] == approx(dt, abs=timer_precision)
    assert res['wall_time_max'] == approx(dt, abs=timer_precision)
    assert res['wall_time_min'] == approx(dt, abs=timer_precision)

    if sys.platform in ['win32', 'darwin']:
        assert res['wall_time_std'] / res['wall_time_mean'] < 0.05
    else:
        assert res['wall_time_std'] / res['wall_time_mean'] < 0.002


def test_memit_overhead():
    res = memit(delayed(sleep)(0.1))
    assert isinstance(res, dict)

    # measurement error is less than 0.15 MB
    assert res['peak_memory_mean'] < 0.15


def test_timeit_sequence():

    res = timeit(delayed(sleep)(0.1) for _ in range(2))
    print(res)


def test_memit_array_allocation():
    np = pytest.importorskip('numpy')

    N = 5000
    double_size = np.ones(1).nbytes

    def allocate_array():
        X = np.ones((N, N))
        sleep(0.1)
        X[:] += 1

    res = memit(delayed(allocate_array)())
    assert res['peak_memory_mean'] == approx(N**2*double_size / 1024**2,
                                             rel=0.01)
