# neurtu, BSD 3 clause license
# Authors: Roman Yurchak


class TagsInferenceException(BaseException):
    pass


def _eval_as_bool(x):
    """Given the result of an equality evaluation
    x = (a == b)
    convert the result to a bool
    """

    if hasattr(x, 'all'):
        x = x.all()

    if isinstance(x, bool):
        return x
    elif x.__class__.__name__ == 'bool_':
        # numpy.bool_ case
        return bool(x)
    elif 'Series' in x.__class__.__name__:
        # pandas.DataFrame reduced to a pandas.Series
        return bool(x.all())
    elif x.__class__.__name__ in ['csr_matrix', 'csc_matrix']:
        return bool(x.data.all())

    raise TagsInferenceException(
            "Could not compute the truth value of %s" % x)


def _check_equal(a, b):
    """Check that two objects are equal

    This also supports numpy like objects
    """
    if id(a) == id(b):
        return True
    res = _eval_as_bool(a == b)
    return res


def _check_equal_dict(a, b):
    """Check that two dictionaries are equal"""
    if set(a.keys()) != set(b.keys()):
        return False
    res = []
    for key in a:
        res.append(_check_equal(a[key], b[key]))
    return all(res)


def _check_equal_all(iterator):
    """Check that all elements in an iterable are equal"""
    iterator = iter(iterator)
    try:
        first = next(iterator)
    except StopIteration:
        return True
    return all(_check_equal_dict(first, rest) for rest in iterator)


def _select_relevant_tags(tags):
    """
    Select the relevant tags from raw tags

    Parameters
    ----------
    tags : list of list of dicts
       input tags

    Returns
    -------
    tags: list of list of dicts
       list of relevant tags
    """

    mask = list(not _check_equal_all(el) for el in zip(*tags))

    return [[inner for idx, inner in enumerate(tags_sample)
             if mask[idx]]
            for tags_sample in tags]
