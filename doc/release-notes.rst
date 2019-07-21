Release notes
=============

Version 0.3
-----------
*July 21, 2019*

API changes
^^^^^^^^^^^

 - Functions to set the number of BLAS threads at runtime were removed
   in favour of using `threadpoolctl
   <https://github.com/joblib/threadpoolctl>`_.

Enhancements
^^^^^^^^^^^^
 - Add ``get_args`` and ``get_kwargs`` to ``Delayed`` object.
 - Better progress bars in Jupyter notebooks with the ``tqdm.auto``
   backend.

Bug fixes
^^^^^^^^^
 - Fix progress bar rendering when ``repeat>1``.
 - Fix warnings due to ``collection.abc``.

Version 0.2
-----------
*August 28, 2018*

New features  
^^^^^^^^^^^^

 - Runtime detection of the BLAS used by numpy `#14 <https://github.com/symerio/neurtu/pull/14>`_
 - Ability to set the number of threads in OpenBlas and
   MKL BLAS at runtime on Linux.  `#15 <https://github.com/symerio/neurtu/pull/15>`_.

Enhancements
^^^^^^^^^^^^
 - Better test coverage
 - Documentation improvements
 - In depth refactoring of the benchmarking code

API changes
^^^^^^^^^^^
 - The API of ``timeit``, ``memit``, ``Benchmark`` changed significantly with respect to v0.1

Version 0.1
-----------
*March 4, 2018*

First release, with support for,

 - wall time, cpu time and peak memory measurements
 - parametric benchmarks using delayed objects
