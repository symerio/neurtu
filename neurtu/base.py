# neurtu, BSD 3 clause license
# Authors: Roman Yurchak

from __future__ import division

import sys
import collections
import timeit as cpython_timeit
import gc

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover
    tqdm = None


from .delayed import _is_delayed
from .compat import _mean, _stddev
from .utils import import_or_none
from .metrics import measure_wall_time, measure_cpu_time
from .metrics import measure_peak_memory


__version__ = '0.1.dev0'


def _validate_timer_precision(res, func, obj_el, params, repeat):
    """For timing measurements, increase the number of iterations
    if the precision is unsufficient"""
    res_mean = _mean(res)
    if sys.platform in ['win32', 'darwin']:  # pragma: no cover
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
        res = []
        for _ in range(repeat):
            gc.collect()
            res.append(func(obj_el, **params))
    return res


class _ProgressBar(object):
    """ Internal progress bar

    Parameters
    ----------
    N : int
      total number of iterations
    delay: {bool, float}
      if a number, and tqdm is installed, display the progress bar when the
      total benchmark time is expected to be larger than the given number of
      seconds. If False, the progress bar is not be displayed.
    """
    def __init__(self, N, delay):
        self.t0 = cpython_timeit.default_timer()
        self.delay = delay
        self.N = N
        self.idx = 0
        self.pbar = None

    def increment(self):
        """
        Decide whether to print a progress bar, update it if necessary
        """
        self.idx += 1
        if tqdm is None or not self.delay:
            pass
        elif self.pbar is None:
            dt = cpython_timeit.default_timer() - self.t0
            if dt * self.N / self.idx > self.delay:
                self.pbar = tqdm(total=self.N)
                self.pbar.update(self.idx)
        else:
            self.pbar.update(1)

    def close(self):
        if self.pbar is not None:
            self.pbar.close()


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
      :func:`measure_cpu_time` function.
    peak_memory : {bool, dict}, default=False
      measure peak memory usage. When a dictionary, it is passed as parameters
      to the :func:`measure_peak_memory` function.
    repeat : int, default=3
        number of repeated measurements
    aggregate : bool, default=True
      whether to aggregate repeated runs.
    to_dataframe : bool, default=None
      whether to convert parametric results to a daframe. By default convert to
      dataframe is pandas is installed.
    progress_bar : {bool, float}, default=5.0
      if a number, and tqdm is installed, display the progress bar when the
      estimated benchmark time is larger than the given number of seconds.
      If False, the progress bar will not be displayed.
    **kwargs : dict
      custom evaluation metrics of the form ``key=func``,
      where ``key`` is the metric name, and the ``func`` is the evaluation
      metric that accepts a ``Delayed`` object: ``func(obj)``.
    """
    def __init__(self, wall_time=None, cpu_time=False, peak_memory=False,
                 repeat=3, aggregate=True, to_dataframe=None,
                 progress_bar=5.0, **kwargs):
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
                raise ValueError(('%s=%s is not a callable. Use a callable '
                                  'to define a custom metric!')
                                 % (name, params))
            params = {'func': params, 'repeat': repeat}
            metrics[name] = params

        if not metrics:
            # if no metrics were explicitly enabled, measure wall_time
            metrics['wall_time'] = {'func': measure_wall_time}
        self.metrics = metrics
        self.aggregate = aggregate
        self.to_dataframe = to_dataframe
        self.progress_bar = progress_bar

    def __call__(self, obj):
        """Evaluate metrics on the delayed object

        Parameters
        ----------
        obj: :class:`Delayed` or iterable of :class:`Delayed`
          a delayed computation or an iterable of delayed computations
        """

        if _is_delayed(obj):
            obj = [obj]
            iterable_input = False
        else:
            iterable_input = True

        if not isinstance(obj, collections.Iterable):
            raise ValueError(('obj=%s must be either a Delayed object or a '
                              'iterable of delayed objects!') % obj)

        # convert the iterable to list
        obj = list(obj)

        tags_all = list(set([self._hash_tags_env(el) for el in obj]))

        # check that tags are unique
        if len(obj) != len(tags_all):
            if len(tags_all) == 1 and tags_all[0] == '':
                raise ValueError('When bechmarking a sequence, please provide '
                                 'the tag parameter for each delayed object '
                                 'to uniquely identify them!')
            else:
                raise ValueError(('Input sequence has %s delayed objects, '
                                  'but only %s unique tags were found!')
                                 % (len(obj), len(tags_all)))

        db = []
        pbar = _ProgressBar(len(obj)*len(self.metrics), self.progress_bar)
        if self.aggregate:
            for idx, obj_el in enumerate(obj):
                db.append(self._evaluate_single_aggregated(obj_el, pbar))
        else:
            for idx, obj_el in enumerate(obj):
                db += self._evaluate_single(obj_el, pbar)
        pbar.close()

        pd = import_or_none('pandas')

        if iterable_input or not self.aggregate:
            if self.to_dataframe is not False and pd is not None:
                return pd.DataFrame(db)
            else:
                return db
        else:
            return db[0]

    def _hash_tags_env(self, obj):
        """Compute a string representation of tags and env of a delayed
        object. This is used for duplicates detection."""
        if not _is_delayed(obj):
            raise ValueError
        tags_el = []
        for key, val in obj.get_tags().items():
            tags_el.append('%s:%s' % (key, val))
        for key, val in obj.get_env().items():
            tags_el.append('%s:%s' % (key, val))
        return '|'.join(tags_el)

    def _evaluate_single(self, obj, pbar):
        """Evaluate a single delayed object"""
        db = []
        for (name, params) in self.metrics.items():
            params = params.copy()
            repeat = params.pop('repeat')
            func = params.pop('func')
            tags = obj.get_tags()
            env = obj.get_env()

            res = []
            for _ in range(repeat):
                gc.collect()
                res.append(func(obj, **params))

            if name in ['wall_time', 'cpu_time']:
                res = _validate_timer_precision(res, func, obj,
                                                params, repeat)
            for k_interation, res_iteration in enumerate(res):
                row = {'repeat': res_iteration, 'metric': name,
                       'value': res_iteration}
                row.update(tags)
                row.update(env)
                db.append(row)
            pbar.increment()
        return db

    def _evaluate_single_aggregated(self, obj, pbar):
        """Evaluate a single delayed object when
        self.aggregated is True"""
        row = {}
        row.update(obj.get_tags())
        row.update(obj.get_env())

        for (name, params) in self.metrics.items():
            params = params.copy()
            repeat = params.pop('repeat')
            func = params.pop('func')

            res = []
            for _ in range(repeat):
                gc.collect()
                res.append(func(obj, **params))

            if name in ['wall_time', 'cpu_time']:
                res = _validate_timer_precision(res, func, obj,
                                                params, repeat)

            row[name + '_min'] = min(res)
            row[name + '_max'] = max(res)
            row[name + '_mean'] = _mean(res)
            if len(res) > 1:
                row[name + '_std'] = _stddev(res)
            pbar.increment()
        return row


def memit(obj, repeat=3, interval=0.01, aggregate=True,
          to_dataframe=None, progress_bar=5.0):
    """Measure the memory use.

    This is an alias for :class:`Benchmark` with `peak_memory=True)`.

    Parameters
    ----------
    repeat : int, default=3
        number of repeated measurements
    aggregate : bool
        aggregate results between repeated measurements
    to_dataframe : bool, default=None
      whether to convert parametric results to a daframe. By default convert to
      dataframe is pandas is installed.
    progress_bar : {bool, float}, default=5.0
      if a number, and tqdm is installed, display the progress bar when the
      estimated benchmark time is larger than the given number of seconds.
      If False, the progress bar will not be displayed.

    Returns
    -------
    res : dict, list or pandas.DataFrame
        computed memory usage
    """

    return Benchmark(peak_memory={'repeat': repeat, 'interval': interval},
                     aggregate=aggregate, to_dataframe=to_dataframe,
                     progress_bar=progress_bar)(obj)


def timeit(obj, timer='wall_time', number=1, repeat=3,
           aggregate=True, to_dataframe=None, progress_bar=5.0):
    """A benchmark decorator

    This is an alias for :class:`Benchmark` with `wall_time=True`.

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
    to_dataframe : bool, default=None
      whether to convert parametric results to a daframe. By default convert to
      dataframe is pandas is installed.
    progress_bar : {bool, float}, default=5.0
      if a number, and tqdm is installed, display the progress bar when the
      estimated benchmark time is larger than the given number of seconds.
      If False, the progress bar will not be displayed.

    Returns
    -------
    res : dict, list or pandas.DataFrame
        computed timing
    """

    args = {'aggregate': aggregate, 'to_dataframe': to_dataframe,
            'progress_bar': progress_bar}

    if timer == 'wall_time':
        return Benchmark(wall_time={'number': number, 'repeat': repeat},
                         **args)(obj)
    elif timer == 'cpu_time':
        return Benchmark(cpu_time={'number': number, 'repeat': repeat},
                         **args)(obj)
    else:
        raise ValueError("timer=%s should be one of 'cpu_time', 'wall_time'"
                         % timer)
