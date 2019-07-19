neurtu
======

|pypi| |rdfd|

|travis| |appveyor| |codecov|

Simple performance measurement tool

neurtu is a Python package providing a common interface for multi-metric benchmarks
(including time and memory measurements). It can can be used to estimate time
and space complexity of algorithms, while pandas integration
allows quick analysis and visualization of the results.

*neurtu* means "to measure / evaluate" in Basque language.

See the `documentation <http://neurtu.readthedocs.io/>`_ for more details.

Installation
------------

neurtu requires Python 2.7 or 3.4+, it can be installed with,

.. code::

   pip install neurtu

`pandas >=0.20 <https://pandas.pydata.org/pandas-docs/stable/install.html#installation>`_ is an optional (but highly recommended) dependency.


Quickstart
----------

To illustrate neurtu usage, will will benchmark array sorting in numpy. First, we will
generator of cases,

.. code:: python

    import numpy as np
    import neurtu

    def cases()
        rng = np.random.RandomState(42)

        for N in [1000, 10000, 100000]:
            X = rng.rand(N)
            tags = {'N' : N}
            yield neurtu.delayed(X, tags=tags).sort()

that yields a sequence of delayed calculations, each tagged with the parameters defining individual runs.

We can evaluate the run time with,

.. code:: python

    >>> df = neurtu.timeit(cases())
    >>> print(df)
            wall_time
    N
    1000     0.000014
    10000    0.000134
    100000   0.001474

which will internally use ``timeit`` module with a sufficient number of evaluation to work around the timer precision
limitations (similarly to IPython's ``%timeit``). It will also display a progress bar for long running benchmarks,
and return the results as a ``pandas.DataFrame`` (if pandas is installed).

By default, all evaluations are run with ``repeat=1``. If more statistical confidence is required, this value can
be increased,

.. code:: python

    >>> neurtu.timeit(cases(), repeat=3)
           wall_time
                mean       max       std
    N
    1000    0.000012  0.000014  0.000002
    10000   0.000116  0.000149  0.000029
    100000  0.001323  0.001714  0.000339

In this case we will get a frame with a
`pandas.MultiIndex <https://pandas.pydata.org/pandas-docs/stable/advanced.html#multiindex-advanced-indexing>`_ for
columns, where the first level represents the metric name (``wall_time``) and the second -- the aggregation method.
By default ``neurtu.timeit`` is called with ``aggregate=['mean', 'max', 'std']`` methods, as supported 
by the `pandas aggregation API <https://pandas.pydata.org/pandas-docs/version/0.22.0/groupby.html#aggregation>`_. To disable,
aggregation and obtains timings for individual runs, use ``aggregate=False``.
See `neurtu.timeit documentation <https://neurtu.readthedocs.io/generated/neurtu.timeit.html>`_ for more details.

To evaluate the peak memory usage, one can use the ``neurtu.memit`` function with the same API,

.. code:: python

    >>> neurtu.memit(cases(), repeat=3)
            peak_memory
                   mean  max  std
    N
    10000           0.0  0.0  0.0
    100000          0.0  0.0  0.0
    1000000         0.0  0.0  0.0

More generally ``neurtu.Benchmark`` supports a wide number of evaluation metrics,

.. code:: python

    >>> bench = neurtu.Benchmark(wall_time=True, cpu_time=True, peak_memory=True)
    >>> bench(cases())
             cpu_time  peak_memory  wall_time
    N
    10000    0.000100          0.0   0.000142
    100000   0.001149          0.0   0.001680
    1000000  0.013677          0.0   0.018347

including `psutil process metrics <https://psutil.readthedocs.io/en/latest/#psutil.Process>`_.

For more information see the `documentation <http://neurtu.readthedocs.io/>`_ and 
`examples <http://neurtu.readthedocs.io/examples/index.html>`_.

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
