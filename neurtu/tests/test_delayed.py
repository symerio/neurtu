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


def test_get_args_kwargs():
    def func(pos_arg, key_arg=None):
        pass

    delayed_obj = delayed(func)('arg', key_arg='kwarg')
    assert delayed_obj.get_args()[0] == 'arg'
    assert delayed_obj.get_kwargs()[0] == {'key_arg': 'kwarg'}
