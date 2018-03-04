Installation
============

neurtu requires Python 2.7 or 3.4+, it can be installed with,

.. code::

   pip install neurtu

`pandas <https://pandas.pydata.org/pandas-docs/stable/install.html#installation>`_ is an optional (but highly recommended) dependency.

.. note::

   the above command will install memory_profiler, shutil (to measure memory use) and tqdm (to make progress bars) mostly for
   convinience. However, neurtu does not have any hard depedencies, it you don't need these functionalites, you can install it
   with ``pip install --no-deps neurtu``
