# neurtu, BSD 3 clause license
# Authors: Roman Yurchak
import os

from neurtu import delayed


def test_set_env():
    def func():
        return os.environ.get('NEURTU_TEST', None)

    assert func() is None

    assert delayed(func, env={'NEURTU_TEST': 'true'})().compute() == 'true'

    assert func() is None
