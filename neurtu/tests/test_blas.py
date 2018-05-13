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
@pytest.mark.skipif(os.name == 'nt',
                    reason='Loading BLAS DLL fails on Windows for now')
@pytest.mark.parametrize('blas_name', ['mkl', 'openblas', 'reference'])
def test_blas_set_threads(blas_name):

    name, dll_path = detect_blas()
    if name != blas_name:
        pytest.skip('blas=%s not found!' % blas_name)

    blas = Blas(dll_path)

    num_threads_0 = blas.get_num_threads()
    assert num_threads_0 > 0
    assert isinstance(num_threads_0, int)

    if 'CI' in os.environ:
        assert num_threads_0 > 1

    num_threads_1 = 1

    # setting the number of threads without a context manager
    blas.set_num_threads(num_threads_1)

    assert blas.get_num_threads() == num_threads_1

    # get back to the original number of threads
    blas.set_num_threads(num_threads_0)

    assert blas.get_num_threads() == num_threads_0

    # setting the number of threads with a context manager

    with blas.set_num_threads(num_threads_1):
        assert blas.get_num_threads() == num_threads_1

    assert blas.get_num_threads() == num_threads_0


@pytest.mark.skipif(np is None, reason='numpy not installed')
@pytest.mark.skipif(os.name == 'nt',
                    reason='Loading BLAS DLL fails on Windows for now')
def test_blas_autodetect():
    blas = Blas()
    name, dll_path = detect_blas()
    assert blas.name == name
    assert blas.dll_path == dll_path


@pytest.mark.skipif(os.name != 'nt',
                    reason='Windows only test')
@pytest.mark.skipif(np is None, reason='numpy not installed')
def test_blas_fails_on_windows():
    with pytest.raises(OSError) as excinfo:
        Blas()
    assert "is not a valid Win32 application" in str(excinfo.value)
