# neurtu, BSD 3 clause license
# Authors: Roman Yurchak

from __future__ import division

import os
import itertools
from glob import glob


def detect_blas(package='numpy'):
    """Detect the BLAS library used by a package

    Note: this assumes that BLAS is dynamically linked and
          that numpy is installed.

    Returns
    -------
    name : str or None
      BLAS implementation, one of openblas, mkl, cblas, None
    dll_path : str or None
      path to the BLAS DLL if available
    """
    if package != 'numpy':
        raise NotImplementedError

    import numpy as np

    blas_opt_info = np.__config__.blas_opt_info

    library_name = [('mkl', 'mkl_rt'),
                    ('openblas', 'openblas'),
                    ('blas', 'blas')  # reference BLAS
                    ]

    for name, library in library_name:
        if library in blas_opt_info['libraries']:
            break
    else:
        return None, None

    dll_path = list(itertools.chain.from_iterable(
                    glob(os.path.join(dirname,
                                      'lib%s*' % dict(library_name)[name]))
                    for dirname in blas_opt_info['library_dirs']))
    if dll_path:
        dll_path = dll_path[0]
    else:
        dll_path = None

    return name, dll_path


class MklBlas(object):
    """Load the MKL BLAS DLL
    """
    def __init__(self, dll_path=None):
        self.dll_path = dll_path

        if not os.path.isfile(dll_path):
            raise IOError('Path %s does not exist!' % dll_path)
