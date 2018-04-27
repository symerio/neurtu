# neurtu, BSD 3 clause license
# Authors: Roman Yurchak

from __future__ import division

import os
from glob import glob
import subprocess

import pytest

from neurtu.blas import detect_blas, Blas
from neurtu.utils import import_or_none
from neurtu.externals.shutil_which import which

conda = which('conda')
ldd = which('ldd')
np = import_or_none('numpy')


@pytest.mark.skipif(np is None, reason='numpy not installed')
def test_detect_blas():
    name, dll_path = detect_blas()
    assert name in ['openblas', 'mkl', 'blas', None]

    if name is not None:
        assert dll_path is not None
        assert os.path.exists(dll_path)

    # Windows
    if conda and os.name == 'nt':
        dependencies = subprocess.check_output([conda, 'list']).decode('utf-8')
        if 'nomkl ' in dependencies and 'openblas' in dependencies:
            assert name == 'openblas'
        elif 'mkl ' in dependencies:
            assert name == 'mkl'

    # Unix
    if ldd and np and os.name != 'nt':
        np_linalg_path = os.path.dirname(np.linalg.__file__)

        # numpy.linalg._umath_linalg.*.so should be present for Numpy 1.7+
        np_linalg_dll = glob(os.path.join(np_linalg_path, '_umath_linalg*'))

        if not np_linalg_dll:
            raise IOError(("Could not find '_umath_linalg* DLL in %s :"
                           "make sure that numpy >=1.7 is installed")
                          % np_linalg_path)

        np_linalg_dll = np_linalg_dll[0]

        linked_libraries = (subprocess.check_output([ldd, np_linalg_dll])
                                      .decode('utf-8'))
        assert 'lib%s' % name in linked_libraries


@pytest.mark.skipif(np is None, reason='numpy not installed')
def test_mkl_set_threads():
    name, dll_path = detect_blas()

    mkl = Blas(name, dll_path)

    mkl.get_version()

    num_threads_0 = mkl.get_num_threads()
    assert num_threads_0 > 0
    assert isinstance(num_threads_0, int)

    num_threads_1 = 1

    mkl.set_num_threads(num_threads_1)

    num_threads_2 = mkl.get_num_threads()
    assert num_threads_2 == num_threads_1


@pytest.mark.skipif(np is None, reason='numpy not installed')
def test_openblas_set_threads():

    mkl = Blas('openblas', "/home/rth/.miniconda3/envs/openblas-env/lib/libopenblas.so")

    num_threads_0 = mkl.get_num_threads()
    print(num_threads_0)
    assert num_threads_0 > 0
    assert isinstance(num_threads_0, int)

    num_threads_1 = 1

    mkl.set_num_threads(num_threads_1)

    num_threads_2 = mkl.get_num_threads()
    assert num_threads_2 == num_threads_1


@pytest.mark.skipif(np is None, reason='numpy not installed')
def test_blasref_set_threads():

    mkl = Blas('blas', "/usr/lib64/libblas.so.3")

    num_threads_0 = mkl.get_num_threads()
    print(num_threads_0)
    assert num_threads_0 > 0
    assert isinstance(num_threads_0, int)

    num_threads_1 = 1

    mkl.set_num_threads(num_threads_1)

    num_threads_2 = mkl.get_num_threads()
    assert num_threads_2 == num_threads_1
