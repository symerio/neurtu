"""
Time complexity of numpy.sort
=============================

In this example we will look into the time complexity of :func:`numpy.sort`

"""

import numpy as np
from neurtu import timeit, delayed


rng = np.random.RandomState(42)


df = timeit(delayed(np.sort, tags={'N': N, 'kind': kind})(rng.rand(N), kind=kind)
            for N in np.logspace(2, 5, num=5).astype('int')
            for kind in ["quicksort", "mergesort", "heapsort"])

print(df.to_string())


##############################################################################
#
# we can use the pandas plotting API (that requires matplotlib)

ax = df.wall_time.unstack().plot(marker='o')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_ylabel('Wall time (s)')
ax.set_title('Time complexity of numpy.sort')
