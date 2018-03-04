# neurtu, BSD 3 clause license
# Authors: Roman Yurchak

from neurtu.utils import import_or_none


def test_import_or_none():
    import os

    os_2 = import_or_none('os')
    assert id(os) == id(os_2)

    pkg = import_or_none('not_existing')
    assert pkg is None
