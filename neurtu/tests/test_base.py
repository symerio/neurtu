from __future__ import division

from time import sleep
from pytest import approx

from neurtu import Benchmark, timeit, memit, delayed


def test_timeit_overhead():

    dt = 0.02

    res = timeit(delayed(sleep)(dt))

    # overhead should be less than 500 us
    assert res['wall_time_mean'] == approx(dt, abs=500e-6)
    assert res['wall_time_max'] == approx(dt, abs=500e-6)
    assert res['wall_time_min'] == approx(dt, abs=500e-6)

    # measurement error should be less than 5%
    assert res['wall_time_std'] / res['wall_time_mean'] < 0.002
    print(res)


def test_memit_overhead():
    res = memit(delayed(sleep)(0.1))
    assert isinstance(res, dict)

    # measurement error is less than 0.15 MB
    assert res['peak_memory_mean'] < 0.15


def test_memit_array_allocation():
    import array
    double_size = 8

    N = 3000

    def allocate_array():
        X = array.array('d')
        X.extend(1.0 for _ in range(N**2))
        sleep(0.1)

    res = memit(delayed(allocate_array)())
    assert res['peak_memory_mean'] == approx(N**2*double_size / 1024**2,
                                             rel=0.01)
