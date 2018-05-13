# neurtu, BSD 3 clause license
# Authors: Roman Yurchak

from __future__ import division

import os
import itertools
import ctypes
from glob import glob
import contextlib
from collections import OrderedDict

BLAS_BACKENDS = OrderedDict([
        ('mkl', ('mkl_rt', 'mkl_core_dll')),
        ('openblas', ('openblas',)),
        ('reference', ('blas',))  # reference BLAS
])


def detect_blas():
    """Detect the BLAS library used by numpy

    Note: this assumes that BLAS is dynamically linked and
          that numpy is installed.

    Returns
    -------
    name : str or None
      BLAS implementation, one of openblas, mkl, cblas, None
    dll_path : str or None
      path to the BLAS DLL if available
    """
    import numpy as np

    blas_opt_info = np.__config__.blas_opt_info

    for name, libraries in BLAS_BACKENDS.items():
        if any(library in blas_opt_info['libraries'] for library in libraries):
            break
    else:
        return None, None

    if os.name == 'posix':
        lib_prefix = 'lib'
    else:
        lib_prefix = ''

    # numpy from PyPi can bundle BLAS and this isn't indicated by np.__config__
    np_lib_builtin = os.path.join(os.path.dirname(np.__file__), '.libs')
    blas_opt_info['library_dirs'].append(np_lib_builtin)

    dll_path = list(itertools.chain.from_iterable(
                    glob(os.path.join(
                         dirname,
                         '%s%s*' % (lib_prefix, library_pattern)))
                    for dirname in blas_opt_info['library_dirs']
                    for library_pattern in BLAS_BACKENDS[name]))

    if dll_path:
        dll_path = dll_path[0]
    else:
        dll_path = None

    return name, dll_path


class Blas(object):
    """Load a BLAS DLL library

    Parameters
    ----------
    dll_path : str, optional
      path to the BLAS dynamc library. If not provided the BLAS used by
      numpy is loaded.
    """
    def __init__(self, dll_path=None):

        if dll_path is None:
            name, dll_path = detect_blas()
            if dll_path is None:
                raise OSError('Could not find any BLAS!')
        else:
            if not os.path.isfile(dll_path):
                raise IOError('Path %s does not exist!' % dll_path)
            dll_name = os.path.basename(dll_path)

            for name, libraries in BLAS_BACKENDS.items():
                if any(library in dll_name for library in libraries):
                    break
            else:
                raise ValueError(('dynamic library %s not recognized '
                                  'as a valid BLAS')
                                 % dll_name)
        self.dll_path = dll_path

        if os.name == 'posix':
            ctypes_loader = ctypes.cdll
        elif os.name == 'nt':
            ctypes_loader = ctypes.windll
        else:
            raise OSError('os.name=%s not supported!' % os.name)

        self.dll = ctypes_loader.LoadLibrary(self.dll_path)
        self.name = name

    def get_num_threads(self):
        """Get the current number of BLAS threads

        Returns
        -------
        N : int
          number of current threads
        """
        mapping = {'openblas': 'get_num_threads',
                   'mkl': 'get_max_threads'}
        if self.name in mapping:
            return self._get_func(mapping[self.name])()
        elif self.name == 'blas':
            return 1
        else:
            raise NotImplementedError('setting the number of threads is not '
                                      'supported on BLAS %s!' % self.name)

    def _get_func(self, function_name):
        return getattr(self.dll, self.name + '_' + function_name)

    def set_num_threads(self, N):
        """Set the maximum number of BLAS threads

        This method can also be used as a context manager.

        Parameters
        ----------
        N : int
          maximum number of BLAS threads

        Examples
        --------
        >>> blas = Blas()   #doctest: +SKIP
        >>> blas.set_num_threads(1)  #doctest: +SKIP
        >>> with blas.set_num_threads(4):  #doctest: +SKIP
        ...     # change the number of threads only in the current context
        ...     pass
        """
        N_init = self.get_num_threads()
        self._set_num_threads(N)

        # if this method is called in a "with" statement,
        # act as a content manager and revert the number of threads to the
        # original version when exiting the context

        @contextlib.contextmanager
        def set_num_threads_context_manager():
            yield
            self._set_num_threads(N_init)

        return set_num_threads_context_manager()

    def _set_num_threads(self, N):
        if N < 1:
            raise ValueError('N=%s must be at least equal to 1' % N)

        if self.name in ['openblas', 'mkl']:
            N_c = ctypes.c_int(N)
            func = self._get_func('set_num_threads')
            if self.name == 'openblas':
                func(N_c)
            elif self.name == 'mkl':
                func(ctypes.byref(N_c))
        elif self.name == 'blas':
            pass
        else:
            raise ValueError
