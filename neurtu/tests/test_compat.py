# neurtu, BSD 3 clause license
# Authors: Roman Yurchak

import pytest
from pytest import approx

from neurtu.compat import _mean, _stddev, mean


def test_compat():
    np = pytest.importorskip('numpy')

    rng = np.random.RandomState(42)

    x = rng.rand(100)

    assert id(mean) == id(np.mean)
    assert id(_mean) != id(np.mean)

    assert x.mean() == approx(_mean(x), rel=1e-9)
    assert x.std() == approx(_stddev(x), rel=1e-9)
