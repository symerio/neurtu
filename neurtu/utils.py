import importlib

# neurtu, BSD 3 clause license
# Authors: Roman Yurchak


def import_or_none(path):
    """Import a package, return None if it's not installed"""
    try:
        pkg = importlib.import_module(path)
        return pkg
    except ImportError:
        return None
