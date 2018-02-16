neurtu
======

Simple performance measurement tool


**Note:** this package is still in early developpement phase, the API may change in the future. Feel free to open an issue for any comments or feedback.

Installation
------------

neurtu requires Python 2.7 or 3.4+, it can be installed with,

.. code::

   pip install git+https://github.com/symerio/neurtu.git

`pandas <https://pandas.pydata.org/pandas-docs/stable/install.html#installation>`_ is an optional (but highly recommended) dependency.


Quickstart
----------

Single benchmark
^^^^^^^^^^^^^^^^
1. Measuring the run time,

   .. code:: python

       from neurtu import timeit, delayed

       timeit(delayed(sum)(range(100000))

   which internally will call the ``timeit.Timer`` class used by ipython.

2. Measuring the memory use,

   .. code:: python

       from neurtu import memit, delayed

       memit(delayed(sorted)(range(100000)))

3. Generic benchmarks

   Both ``timeit`` and ``memit`` are aliases for the ``Benchmark`` class which can be used for

   .. code:: python

       from neurtu import Benchmark, delayed

       Benchmark(wall_time=True, peak_memory=True)(
              delayed(sorted)(range(100000)), number=100)



Parametric benchmarks
^^^^^^^^^^^^^^^^^^^^^

Delayed evaluation
^^^^^^^^^^^^^^^^^^

The ``delayed`` function follows the `dask.delayed <http://dask.pydata.org/en/latest/delayed-api.html>`_ API, though with a significantly lighter functionality: it models operations as a chained list of delayed objects that are not evaluated untill the ``compute()`` method is called.

.. code:: python

  >>> from neurtu import delayed
  >>> x = delayed('some string').split(' ')[::-1]
  >>> x
  <Delayed('some string')>
   ->.split
   ->( )
   ->[slice(None, None, -1)]
  >>> x.compute()
  ['string', 'some']

Attrubute access, indexing as well as function and method calls are supported. 
Left function composition (e.g. ``func(delayed(obj))``) and binary operations (e.g. ``delayed(op) + 1``) are currently not supported, neither is the composition of multiple delayed objects, use `dask.delayed` for it.


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
