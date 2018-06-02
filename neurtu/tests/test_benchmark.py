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

    assert res['wall_time'] == approx(dt, abs=timer_precision)


def test_wall_user_time():
    pytest.importorskip('resource')

    res = timeit(delayed(sleep)(0), timer='cpu_time')
    assert 'cpu_time' in res


# Memory based tests


def test_memit_overhead():
    res = memit(delayed(sleep)(0.1))
    assert isinstance(res, dict)

    # measurement error is less than 1.0 MB
    assert res['peak_memory'] < 1.0


def test_memit_array_allocation():
    np = pytest.importorskip('numpy')

    N = 5000
    double_size = np.ones(1).nbytes

    def allocate_array():
        X = np.ones((N, N))
        sleep(0.1)
        X[:] += 1

    res = memit(delayed(allocate_array)())
    assert res['peak_memory'] == approx(N**2*double_size / 1024**2,
                                        rel=0.05)


@pytest.mark.parametrize('repeat', (1, 3))
@pytest.mark.parametrize('aggregate', [['mean', 'max'], False])
def test_dataframe_conversion(repeat, aggregate):

    pd = pytest.importorskip('pandas')

    N = 2

    metrics = ['peak_memory', 'wall_time']

    bench = Benchmark(wall_time=True, peak_memory=True,
                      repeat=repeat, aggregate=aggregate)

    res = bench(delayed(sleep, tags={'idx': idx})(0.04) for idx in range(N))

    assert isinstance(res, pd.DataFrame)

    if aggregate:
        assert len(res) == N
        assert res.index.names == ['idx']
        if repeat > 1:
            assert isinstance(res.columns, pd.MultiIndex)
            assert list(res.columns.levels[0]) == metrics
            assert list(res.columns.levels[1]) == aggregate
        else:
            assert isinstance(res.columns, pd.Index)
    else:
        assert len(res) == N*repeat
        if repeat > 1:
            assert res.index.names == ['idx', 'runid']
        else:
            assert res.index.names == ['idx']
        assert isinstance(res.columns, pd.Index)
        assert list(res.columns) == metrics


# Handling of optional parameters

def test_repeat():

    agg = ('mean',)
    res = timeit(delayed(sleep)(0), repeat=2, aggregate=agg)
    pd = import_or_none('pandas')

    if pd is None:
        assert len(res) == 2
    else:
        assert list(res.columns) == ['wall_time']
        assert list(res.index) == list(agg)


@pytest.mark.parametrize('repeat', (1, 2))
def test_multiple_metrics(repeat):

    bench = Benchmark(wall_time=True, peak_memory=True,
                      to_dataframe=False, repeat=repeat)
    res = bench(delayed(sleep)(0))

    if repeat == 1:
        assert isinstance(res, dict)
    else:
        assert isinstance(res, list)
        len(res) == repeat
        assert isinstance(res[0], dict)
        res = res[0]

    for metric in ['wall_time', 'peak_memory']:
        assert metric in res
        assert res[metric] >= 0


def test_benchmark_env():

    res = timeit(delayed(sleep, env={'NEURTU_TEST': 'true'})(0))
    assert 'NEURTU_TEST' in res
    assert res['NEURTU_TEST'] == 'true'

# Parametric benchmark testing


@pytest.mark.parametrize('repeat', (1, 2))
def test_timeit_sequence(repeat):

    res = timeit((delayed(sleep, tags={'idx': idx})(0.1) for idx in range(2)),
                 repeat=repeat, to_dataframe=False)
    assert isinstance(res, list)
    for row in res:
        assert 'wall_time' in row
        assert row['wall_time'] > 0


def test_untaged_sequence():

    with pytest.raises(ValueError) as excinfo:
        timeit(delayed(sleep)(0.1) for _ in range(2))
    assert "please provide the tag parameter" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        timeit([delayed(sleep, tags={'a': 1})(0.1),
                delayed(sleep, tags={'a': 1})(0.1)])
    assert "but only 1 unique tags were found" in str(excinfo.value)


def test_progress_bar(capsys):
    timeit((delayed(sleep, tags={'N': idx})(0.1) for idx in range(2)),
           repeat=1)
    out, err = capsys.readouterr()
    out = out + err
    assert len(out) == 0
    timeit((delayed(sleep, tags={'N': idx})(0.1) for idx in range(2)),
           progress_bar=1e-3, repeat=1)
    out, err = capsys.readouterr()
    out = out + err
    assert len(out) > 0
    assert '100%' in out
    assert '2/2' in out


def test_custom_metric():
    with pytest.raises(ValueError) as excinfo:
        Benchmark(other_timer=True)(delayed(sleep)(0.1))
    assert 'other_timer=True is not a callable' in str(excinfo.value)

    def custom_metric(obj):
        return sum(obj.compute())

    bench = Benchmark(custom_metric=custom_metric)
    res = bench(delayed(range)(3))
    assert res == {'custom_metric': 3}
