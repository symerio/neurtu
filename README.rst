neurtu
======

.. image:: https://travis-ci.org/symerio/neurtu.svg?branch=master
    :target: https://travis-ci.org/symerio/neurtu

.. image:: https://ci.appveyor.com/api/projects/status/947sx73ph2v4v7ej?svg=true
    :target: https://ci.appveyor.com/project/rth/neurtu/branch/master

Simple performance measurement tool


**Note:** this package is still in early developpement phase, the API may change in the future. Feel free to open an issue for any comments or feedback.

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

   which will internally cll the ``timeit.Timer`` class. Similarly to IPython's ``%timeit``, the number of runs
   will be determined at runtime to mitigate the finite resolution of the timer (on Windows it's 16 ms!). In addition,
   each evaluation will be here repeated 3 times (default) to measure statistics.

2. Similarity, the memory use can be measured with,

   .. code:: python

       >>> from neurtu import memit, delayed
       >>> memit(delayed(sorted)(list(range(100000))))
       {'peak_memory_max': 0.765, 'peak_memory_mean': 0.757, 'peak_memory_min': 0.753, 'peak_memory_std': 0.00552}

3. Generic benchmarks

   Both ``timeit`` and ``memit`` are aliases for the ``Benchmark`` class which can be used with one or several metrics,

   .. code:: python

       from neurtu import Benchmark, delayed

       Benchmark(wall_time=True, peak_memory=True)(
              delayed(sorted)(range(100000)), number=3)


   Currently supported metrics are ``wall_time``, ``peak_memory`` as well as ``cpu_time`` (Linux and Mac OS only).



Parametric benchmarks
^^^^^^^^^^^^^^^^^^^^^

The ``timeit``, ``memit`` and ``Benchmark`` also accept as input sequence of delayed objects, tagged with the ``tags`` parameter,

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

The ``delayed`` function is a partial implementation of the `dask.delayed <http://dask.pydata.org/en/latest/delayed-api.html>`_ API. It models operations as a chained list of delayed objects that are not evaluated untill the ``compute()`` method is called.

.. code:: python

  >>> from neurtu import delayed
  >>> x = delayed('some string').split(' ')[::-1]
  >>> x
  <Delayed('some string').split(' ')[slice(None, None, -1)]>
  >>> x.compute()
  ['string', 'some']

Attrubute access, indexing as well as function and method calls are supported. 
Left function composition (e.g. ``func(delayed(obj))``) and binary operations (e.g. ``delayed(op) + 1``) are currently not supported, neither is the composition of multiple delayed objects, use `dask.delayed` for those.


Scientific computing usage
^^^^^^^^^^^^^^^^^^^^^^^^^^

A typical use case, occurs when manipulating objects with a scikit-learn API,

.. code:: python

    res = Benchmark(wall_time=True, cpu_time=True)(
            delayed(NearestNeighbors, tags={'n_jobs': n_jobs})(n_jobs=n_jobs).fit(X)
            for n_jobs in range(1, 10))



Motivation
----------

The API was strongly inspired by `joblib.Parallel <https://pythonhosted.org/joblib/parallel.html>`_. 


The package name was taken from the Basque word *neurtu* meaning "to measure / evaluate". 


License
-------

neurtu is released under the 3-clause BSD license.
