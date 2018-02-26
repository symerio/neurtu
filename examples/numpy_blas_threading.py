"""
Number BLAS threads used for matrix multiplication
===================================================

This example illustrate to evaluate the performance impact of the number
of BLAS threads used for matrix inversion
"""
import multiprocessing

import numpy as np
import matplotlib.pyplot as plt

from neurtu import Benchmark, delayed

##############################################################################
#
# Information about BLAS used with numpy is given below,

print(np.__config__.show())


##############################################################################
#
# This example is run on a machine with the following number of logical
# CPU cores,

print(multiprocessing.cpu_count())


##############################################################################
#
# Let's run matrix inversion

X = np.random.RandomState(42).rand(2000, 2000)

bench = Benchmark(wall_time=True, cpu_time=True)

res = bench(delayed(X, env={'OMP_NUM_THREADS': str(k)}).dot(X)
            for k in range(1, multiprocessing.cpu_count() + 1))
print(res)

fig, ax = plt.subplots(1, 1)
ax.errorbar(res.OMP_NUM_THREADS, res.wall_time_mean,
            yerr=[res.wall_time_mean - res.wall_time_min,
                  res.wall_time_max - res.wall_time_mean],
            fmt='--o', label='Wall time')
ax.errorbar(res.OMP_NUM_THREADS, res.cpu_time_mean,
            yerr=[res.cpu_time_mean - res.cpu_time_min,
                  res.cpu_time_max - res.cpu_time_mean],
            fmt='--o', label='CPU time')
ax.set_xlabel('OMP_NUM_THREADS')
ax.set_ylabel('Time (s)')
ax.legend(loc=1)
ax.set_ylim(ymin=0)
