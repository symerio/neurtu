# neurtu, BSD 3 clause license
# Authors: Roman Yurchak

from __future__ import division

import itertools
import timeit as cpython_timeit
import gc


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
    except ImportError:  # pragma: no cover
        raise ValueError('CPU timer is not available on Windows.')
    timer = Timer(obj.compute, timer=timer)
    dt = timer.timeit(number)
    return dt / number


def measure_peak_memory(obj, **kwargs):
    from memory_profiler import memory_usage as _memory_usage_profiler
    usage = _memory_usage_profiler((obj.compute, (), {}), **kwargs)
    # subtract the initial memory usage of the process
    usage = [el - usage[0] for el in usage]
    return max(usage)
