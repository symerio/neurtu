Quickstart
==========

Single benchmark
^^^^^^^^^^^^^^^^
1. Measuring the run time,

   .. code:: python

       >>> from neurtu import timeit, delayed
       >>> timeit(delayed(sum)(range(100000)), repeat=3)
       {'wall_time_max': 0.0018, 'wall_time_mean': 0.0017, 'wall_time_min': 0.0015, 'wall_time_std': 0.00011}

   which will internally call :class:`timeit.Timer`. Similarly to IPython's ``%timeit``, the number of runs
   will be determined at runtime to mitigate the finite resolution of the timer (on Windows it's 16 ms!). In addition,
   each evaluation will be here repeated 3 times (default) to measure statistics.

2. Similarity, the memory use can be measured with,

   .. code:: python

       >>> from neurtu import memit, delayed
       >>> memit(delayed(sorted)(list(range(100000))))
       {'peak_memory_max': 0.765, 'peak_memory_mean': 0.757, 'peak_memory_min': 0.753, 'peak_memory_std': 0.00552}

3. Generic benchmarks

   Both :func:`timeit` and :func:`memit` are aliases for the :class:`Benchmark` class which can be used with one or several metrics,

   .. code:: python

       from neurtu import Benchmark, delayed

       Benchmark(wall_time=True, peak_memory=True)(
              delayed(sorted)(range(100000)), number=3)


   Currently supported metrics are ``wall_time``, ``peak_memory`` as well as ``cpu_time`` (Linux and Mac OS only).



Parametric benchmarks
^^^^^^^^^^^^^^^^^^^^^

The :func:`timeit`, :func:`memit` and :class:`Benchmark`` also accept as input sequence of delayed objects, tagged with the ``tags`` parameter,

.. code:: python

    >>> from neurtu import timeit, delayed
    >>> timeit(delayed(sorted, tags={'N': N})(range(N)) for N in [1000, 10000, 100000])
            N  wall_time_max  wall_time_mean  wall_time_min  wall_time_std
    0    1000       0.000024        0.000024       0.000024   5.951794e-08
    1   10000       0.000319        0.000319       0.000318   4.723035e-07
    2  100000       0.003695        0.003686       0.003678   7.144085e-06


which will produce a ``pandas.DataFrame`` with the measures if pandas is installed and a list of dictionaries otherwise.

     

Delayed evaluation
^^^^^^^^^^^^^^^^^^

The :func:`delayed`` function is a partial implementation of the :func:`dask.delayed` API. It models operations as a chained list of delayed objects that are not evaluated untill the ``compute()`` method is called.

.. code:: python

  >>> from neurtu import delayed
  >>> x = delayed('some string').split(' ')[::-1]
  >>> x
  <Delayed('some string').split(' ')[slice(None, None, -1)]>
  >>> x.compute()
  ['string', 'some']

Attrubute access, indexing as well as function and method calls are supported. 
Left function composition (e.g. ``func(delayed(obj))``) and binary operations (e.g. ``delayed(op) + 1``) are currently not supported, neither is the composition of multiple delayed objects, use :func:`dask.delayed` for those.
