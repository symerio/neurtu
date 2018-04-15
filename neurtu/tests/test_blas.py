# neurtu, BSD 3 clause license
# Authors: Roman Yurchak

from __future__ import division

import os
from glob import glob
import subprocess

from neurtu.blas import detect_blas
from neurtu.utils import import_or_none
from neurtu.externals.shutil_which import which

conda = which('conda')
ldd = which('ldd')
np = import_or_none('numpy')


def test_detect_blas():
    name, dll_path = detect_blas()
    assert name in ['openblas', 'mkl', 'blas', None]
    if name is not None:
        assert os.path.exists(dll_path)

    # Windows
    if conda and os.name == 'nt':
        dependencies = subprocess.check_output([conda, 'list']).decode('utf-8')
        if 'nomkl ' in dependencies and 'openblas' in dependencies:
            assert name == 'openblas'
        elif 'mkl ' in dependencies:
            assert name == 'mkl'

    # Unix
    if ldd and np:
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
