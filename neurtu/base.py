from __future__ import division

import sys
import timeit as cpython_timeit
import itertools
from functools import partial
import collections

import gc

from .delayed import _is_delayed
from .compat import _mean, _stddev

__version__ = '0.1.dev0'


# Timer class copied from ipython

class Timer(cpython_timeit.Timer):
    """Timer class that explicitly uses self.inner

    which is an undocumented implementation detail of CPython,
    not shared by PyPy.
    """
    # Timer.timeit copied from CPython 3.4.2
    def timeit(self, number=cpython_timeit.default_number):
        """Time 'number' executions of the main statement.
        To be precise, this executes the setup statement once, and
        then returns the time it takes to execute the main statement
        a number of times, as a float measured in seconds.  The
        argument is the number of times through the loop, defaulting
        to one million.  The main statement, the setup statement and
        the timer function to be used are passed to the constructor.
        """
        it = itertools.repeat(None, number)
        gcold = gc.isenabled()
        gc.disable()
        try:
            timing = self.inner(it, self.timer)
        finally:
            if gcold:
                gc.enable()
        return timing


def measure_wall_time(obj, number=1):
    timer = Timer(obj.compute, timer=cpython_timeit.default_timer)
    dt = timer.timeit(number)
    return dt / number


def measure_cpu_time(obj, number=1):
    try:
        import resource

        def timer():
            return resource.getrusage(resource.RUSAGE_SELF).ru_utime
    except ImportError:
        raise NotImplementedError('CPU timer is not available on Windows.')
    timer = Timer(obj.compute, timer=timer)
    dt = timer.timeit(number)
    return dt / number


def measure_peak_memory(obj, **kwargs):
    from memory_profiler import memory_usage as _memory_usage_profiler
    usage = _memory_usage_profiler((obj.compute, (), {}), **kwargs)
    # subtract the initial memory usage of the process
    usage = [el - usage[0] for el in usage]
    return max(usage)


class Benchmark(object):
    """Benchmark calculations

    Parameters
    ----------
    wall_time : {bool, dict}, default=None
      measure wall time. When a dictionary, it is passed as parameters to the
      `func:measure_wall_time` function. Will default to True, unless some
      other metric is enabled.
    cpu_time : {bool, dict}, default=False
      measure CPU time. When a dictionary, it is passed as parameters to the
    `func:measure_cpu_time` function.
    peak_memory : {bool, dict}, default=False
      measure peak memory usage. When a dictionary, it is passed as parameters
      to the `func:measure_peak_memory` function.
    repeat : int, default=3
        number of repeated measurements
    aggregate : bool, default=True
      whether to aggregate repeated runs.
    to_dataframe : bool, default=None
      whether to convert parametric results to a daframe
    **kwargs : dict
      custom evaluation metrics of the form ``key=func``,
      where ``key`` is the metric name, and the ``func`` is the evaluation
      metric that accepts a ``Delayed`` object: ``func(obj)``.
    """
    def __init__(self, wall_time=None, cpu_time=False, peak_memory=False,
                 repeat=3, aggregate=True, to_dataframe=None, **kwargs):
        metrics = {}
        for name, params, func in [
                ('wall_time', wall_time, measure_wall_time),
                ('cpu_time', cpu_time, measure_cpu_time),
                ('peak_memory', peak_memory, measure_peak_memory)]:
            if params:
                if params is True:
                    params = {'repeat': repeat}
                else:
                    params = params.copy()
                    if 'repeat' not in params:
                        # if the individual repeat parameter is not defined,
                        # use the global one
                        params['repeat'] = repeat
                params['func'] = func
                metrics[name] = params
        for name, params in kwargs.items():
            if not callable(params):
                raise ValueError('%s=%s is not a callable. Use a callable '
                                 'to define a custom metric!')
        if not metrics:
            # if no metrics were explicitly enabled, measure wall_time
            metrics['wall_time'] = {'func': measure_wall_time}
        self.metrics = metrics
        self.aggregate = aggregate
        self.to_dataframe = to_dataframe

    def __call__(self, obj):
        """Evaluate metrics on the delayed object

        Parameters
        ----------
        obj: `class:Delayed` or iterable of `class:Delayed`
          a delayed computation or an iterable of delayed computations
        """
        try:
            from tqdm import tqdm
        except ImportError:

            def tqdm(x):
                return x
        if _is_delayed(obj):
            obj = [obj]
            iterable_input = False
        else:
            iterable_input = True

        if not isinstance(obj, collections.Iterable):
            raise ValueError(('obj=%s must be either a Delayed object or a '
                              'iterable of delayed objects!') % obj)

        db = []
        for obj_el, (name, params) in itertools.product(
                obj, self.metrics.items()):
            params = params.copy()
            repeat = params.pop('repeat', 3)
            func = params.pop('func')
            func_partial = partial(func, **params)
            tags = obj_el.get_tags()

            res = [func_partial(obj_el) for _ in range(repeat)]

            if name in ['wall_time', 'cpu_time']:
                res_mean = _mean(res)
                if sys.platform in ['win32', 'darwin']:
                    timer_threashold = 1.0
                else:
                    timer_threashold = 0.2
                if res_mean < timer_threashold:
                    # if the measured timeing is below the threashold,
                    # it won't be very accurate. Increase the
                    # `number` parameter of Timer.timeit to get
                    # result in the order of 500 ms

                    corrected_number = int(timer_threashold / res_mean)
                    params = params.copy()
                    params['number'] = corrected_number
                    func_partial = partial(func, **params)
                    res = [func_partial(obj_el) for _ in range(repeat)]

            if self.aggregate:
                row = {name + '_min': min(res),
                       name + '_max': max(res),
                       name + '_mean': _mean(res),
                       }
                if len(res) > 1:
                    row[name + '_std'] = _stddev(res)
                row.update(tags)
                db.append(row)
            else:
                for k_interation, res_iteration in enumerate(res):
                    row = {name: res_iteration}
                    row.update(tags)
                    db.append(row)

        try:
            import pandas as pd
        except ImportError:
            pd = None

        if iterable_input:
            if self.to_dataframe is not False and pd is not None:
                return pd.DataFrame(db)
            else:
                return db
        else:
            return db[0]


def memit(obj, repeat=3, interval=0.01, aggregate=True):
    """Measure the memory use.

    This is an alias for `class:Benchmark(peak_memory=True)`.

    Parameters
    ----------
    repeat : int, default=3
        number of repeated measurements
    aggregate : bool
        aggregate results between repeated measurements
    """

    return Benchmark(peak_memory={'repeat': repeat, 'interval': interval},
                     aggregate=aggregate)(obj)


def timeit(obj, timer='wall_time', number=1, repeat=3,
           aggregate=True):
    """A benchmark decorator

    This is an alias for `class:Benchmark(wall_time=True)`.

    Parameters
    ----------
    obj : {Delayed, iterable of Delayed}
        delayed object to compute, or an iterable of Delayed objects
    number : int, default=1
        number of runs to pass to ``timeit.Timer``
    repeat : int, default=3
        number of repeated measurements
    aggregate : bool
        aggregate results between repeated measurements

    Returns
    -------
    res : list or pandas.DataFrame
        computed timing
    """

    if timer == 'wall_time':
        return Benchmark(wall_time={'number': number, 'repeat': repeat},
                         aggregate=aggregate)(obj)
    elif timer == 'cpu_time':
        return Benchmark(cpu_time={'number': number, 'repeat': repeat},
                         aggregate=aggregate)(obj)
    else:
        raise ValueError("timer=%s should be one of 'cpu_time', 'wall_time'"
                         % timer)
