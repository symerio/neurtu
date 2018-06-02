"""
LogisticRegression scaling in scikit-learn
==========================================

In this example we will look into the time and space complexity of
:class:`sklearn.linear_model.LogisticRegression`

"""

import numpy as np
from sklearn.linear_model import LogisticRegression
from neurtu import Benchmark, delayed


rng = np.random.RandomState(42)

n_samples, n_features = 50000, 100


X = rng.rand(n_samples, n_features)
y = rng.randint(2, size=(n_samples))


def benchmark_cases():
    for N in np.logspace(np.log10(100), np.log10(n_samples), 5).astype('int'):
        for solver in ['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga']:
            tags = {'N': N, 'solver': solver}
            model = delayed(LogisticRegression, tags=tags)(
                                solver=solver, random_state=rng)

            yield model.fit(X[:N], y[:N])


bench = Benchmark(wall_time=True, peak_memory=True)
df = bench(benchmark_cases())

print(df.tail())


##############################################################################
#
# The above section will run in approximately 1min, a progress bar will be
# displayed.
#
# We can use the pandas plotting API (that requires matplotlib) to visualize
# the results,

ax = df.wall_time.unstack().plot(marker='o')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_ylabel('Wall time (s)')
ax.set_title('Run time scaling for LogisticRegression.fit')


##############################################################################
#
# The solver with the best scalability in this example is "lbfgs".
#
# Similarly the memory scaling is represented below,

ax = df.peak_memory.unstack().plot(marker='o')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_ylabel('Peak memory (MB)')
ax.set_title('Peak memory usage for LogisticRegression.fit')

##############################################################################
#
# Peak memory usage for "liblinear" and "newton-cg" appear to be significant
# above 10000 samples, while the other solvers
# use less memory than the detection threshold.
# Note that these benchmarks do not account for the memory used by ``X`` and
# ``y`` arrays.
