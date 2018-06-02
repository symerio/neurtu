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


def test_infer_tags():
    obj = delayed(None)(x=1)
    assert obj.get_tags(infer=True) == [{'x': 1}]

    obj = delayed(None)(y='ze').get(x=3)
    assert obj.get_tags(infer=True) == [{'x': 3}, {'y': "ze"}]

    obj = delayed(None)(1)
    assert obj.get_tags(infer=True) == [{'arg_0': 1}]

    obj = delayed(None)(a=1)[23]
    assert obj.get_tags(infer=True) == [{'arg_0': 23}, {'a': 1}]
