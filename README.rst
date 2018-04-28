neurtu
======

|pypi| |rdfd|

|travis| |appveyor| |codecov|

Simple performance measurement tool

neurtu is a Python benchmarking library with a unified interface for time and memory
measurements. It aims to provide a convenient API similar to IPython's
``%timeit`` magic command, but based on delayed evaluation. Parametric benchmarks
can be used to estimate time and space complexity of algorithms, while pandas integration
allows quick analysis and visualization of the results.

*neurtu* means "to measure / evaluate" in Basque language.

See the `documentation <http://neurtu.readthedocs.io/>`_ for more details.

Installation
------------

neurtu requires Python 2.7 or 3.4+, it can be installed with,

.. code::

   pip install neurtu

`pandas <https://pandas.pydata.org/pandas-docs/stable/install.html#installation>`_ is an optional (but highly recommended) dependency.


Quickstart
----------

Single benchmark
^^^^^^^^^^^^^^^^
1. Measuring the run time,

   .. code:: python

       >>> from neurtu import timeit, delayed
       >>> timeit(delayed(sum)(range(100000)), repeat=3)
       {'wall_time_max': 0.0018, 'wall_time_mean': 0.0017, 'wall_time_min': 0.0015, 'wall_time_std': 0.00011}

   which will internally call ``timeit.Timer``. Similarly to IPython's ``%timeit``, the number of runs
   will be determined at runtime to mitigate the finite resolution of the timer (on Windows it's 16 ms!). In addition,
   each evaluation will be repeated 3 times to measure run time statistics.

2. Similarly, the memory use can be measured with,

   .. code:: python

       >>> from neurtu import memit, delayed
       >>> memit(delayed(sorted)(list(range(100000))))
       {'peak_memory_max': 0.765, 'peak_memory_mean': 0.757, 'peak_memory_min': 0.753, 'peak_memory_std': 0.00552}

3. Generic benchmarks

   Both ``timeit`` and ``memit`` are aliases for the ``Benchmark`` class which can be used with one or several metrics,

   .. code:: python

       from neurtu import Benchmark, delayed

       Benchmark(wall_time=True, peak_memory=True)(
              delayed(sorted)(range(100000)))


   Currently supported metrics are ``wall_time``, ``peak_memory`` as well as ``cpu_time`` (Linux and Mac OS only).



Parametric benchmarks
^^^^^^^^^^^^^^^^^^^^^

The ``timeit``, ``memit`` and ``Benchmark`` also accept as input sequence of delayed objects, tagged with the ``tags`` parameter.
This can typically be used to determine time or space complexity of some calculation,

.. code:: python

    >>> from neurtu import timeit, delayed
    >>> timeit(delayed(sorted, tags={'N': N})(range(N))
    ...        for N in [1000, 10000, 100000])
            N  wall_time_max  wall_time_mean  wall_time_min  wall_time_std
    0    1000       0.000024        0.000024       0.000024   5.951794e-08
    1   10000       0.000319        0.000319       0.000318   4.723035e-07
    2  100000       0.003695        0.003686       0.003678   7.144085e-06


the results with be a ``pandas.DataFrame`` if pandas is installed and a list of dictionaries otherwise.

In general, we can pass any iterable to the benchmark functions. For instance the above example is equivalent to,
  
.. code:: python

    >>> from neurtu import timeit, delayed
    >>> def delayed_cases():
    ...     for N in [1000, 10000, 100000]:
    ...         yield delayed(sorted, tags={'N': N})(range(N))
    >>> timeit(delayed_cases())
     

Delayed evaluation
^^^^^^^^^^^^^^^^^^

Instead of working with a string statement or a callable as ``timeit.Timer`` does, neurtu evaluates delayed objects.

The ``delayed`` function is a partial implementation of the `dask.delayed <http://dask.pydata.org/en/latest/delayed-api.html>`_ API. It models operations as a chained list of delayed operations that are not evaluated until the ``compute()`` method is called.

.. code:: python

  >>> from neurtu import delayed
  >>> x = delayed('some string').split(' ')[::-1]
  >>> x
  <Delayed('some string').split(' ')[slice(None, None, -1)]>
  >>> x.compute()
  ['string', 'some']

Attribute access, indexing as well as function and method calls are supported. 
Left function composition (e.g. ``func(delayed(obj))``) and binary operations (e.g. ``delayed(op) + 1``) are currently not supported, neither is the composition of multiple delayed objects, use `dask.delayed` for those.


Scientific computing usage
^^^^^^^^^^^^^^^^^^^^^^^^^^

A typical use case, occurs when manipulating objects with a scikit-learn API,

.. code:: python

    res = Benchmark(wall_time=True, cpu_time=True)(
            delayed(NearestNeighbors, tags={'n_jobs': n_jobs})(n_jobs=n_jobs).fit(X)
            for n_jobs in range(1, 10))


License
-------

neurtu is released under the 3-clause BSD license.


.. |pypi| image:: https://img.shields.io/pypi/v/neurtu.svg
    :target: https://pypi.python.org/pypi/neurtu

.. |rdfd| image:: https://readthedocs.org/projects/neurtu/badge/?version=latest
    :target: http://neurtu.readthedocs.io/

.. |travis| image:: https://travis-ci.org/symerio/neurtu.svg?branch=master
    :target: https://travis-ci.org/symerio/neurtu

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/2i1dx8fi3bue4qwl?svg=true
    :target: https://ci.appveyor.com/project/rth/neurtu/branch/master

.. |codecov| image:: https://codecov.io/gh/symerio/neurtu/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/symerio/neurtu
