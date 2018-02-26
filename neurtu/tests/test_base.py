# neurtu, BSD 3 clause license
# Authors: Roman Yurchak

from __future__ import division

import sys
from time import sleep
import pytest
from pytest import approx

from neurtu import timeit, memit, delayed, Benchmark
from neurtu.utils import import_or_none

# Timing tests


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
        assert res['wall_time_std'] / res['wall_time_mean'] < 0.1
    else:
        assert res['wall_time_std'] / res['wall_time_mean'] < 0.01


def test_wall_user_time():
    pytest.importorskip('resource')

    res = timeit(delayed(sleep)(0), timer='cpu_time')
    assert 'cpu_time_mean' in res


# Memory based tests


def test_memit_overhead():
    res = memit(delayed(sleep)(0.1))
    assert isinstance(res, dict)

    # measurement error is less than 0.15 MB
    assert res['peak_memory_mean'] < 0.15


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


@pytest.mark.parametrize('aggregate', ['aggregate', None])
def test_dataframe_conversion(aggregate):

    pd = import_or_none('pandas')

    N = 2
    repeat = 3
    aggregate = aggregate is not None

    res = timeit((delayed(sleep, tags={'idx': idx})(0.1) for idx in range(N)),
                 aggregate=aggregate, repeat=repeat)

    if pd is None:
        assert isinstance(res, list)
        if aggregate:
            assert len(res) == N
        else:
            assert len(res) == N*repeat

    else:
        assert isinstance(res, pd.DataFrame)
        if aggregate:
            assert res.shape[0] == N
        else:
            assert res.shape[0] == N*repeat

# Handling of optional parameters


def test_multiple_metrics():

    bench = Benchmark(wall_time=True, peak_memory=True)
    res = bench(delayed(sleep)(0))
    assert isinstance(res, dict)
    for metric in ['wall_time', 'peak_memory']:
        for key in ['min', 'max', 'mean', 'std']:
            name = '_'.join([metric, key])
            assert name in res
            assert res[name] >= 0


def test_non_aggregated():
    res = timeit(delayed(sleep)(0), to_dataframe=False,
                 aggregate=False)

    assert isinstance(res, list)
    for row in res:
        assert set(row.keys()) == set(['value', 'metric', 'repeat'])


def test_benchmark_env():

    res = timeit(delayed(sleep, env={'NEURTU_TEST': 'true'})(0))
    assert 'NEURTU_TEST' in res
    assert res['NEURTU_TEST'] == 'true'

# Parametric benchmark testing


def test_timeit_sequence():

    res = timeit((delayed(sleep, tags={'idx': idx})(0.1) for idx in range(2)),
                 to_dataframe=False)
    assert isinstance(res, list)
    for row in res:
        for key in ['min', 'max', 'mean', 'std']:
            name = 'wall_time_' + key
            assert name in row
            assert row[name] > 0


def test_untaged_sequence():

    with pytest.raises(ValueError) as excinfo:
        timeit(delayed(sleep)(0.1) for _ in range(2))
    assert "please provide the tag parameter" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        timeit([delayed(sleep, tags={'a': 1})(0.1),
                delayed(sleep, tags={'a': 1})(0.1)])
    assert "but only 1 unique tags were found" in str(excinfo.value)
