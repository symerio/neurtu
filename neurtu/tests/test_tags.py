# neurtu, BSD 3 clause license
# Authors: Roman Yurchak

import pytest

from neurtu.tags import _select_relevant_tags, _eval_as_bool


def test_select_relevant_tags():

    tags = [[{'a': 1}, {'b': 2}],
            [{'a': 2}, {'b': 2}]]

    tags_relevant = _select_relevant_tags(tags)
    assert tags_relevant == [[{'a': 1}], [{'a': 2}]]


def test_select_relevant_tags_numpy():
    np = pytest.importorskip('numpy')

    x = np.ones(10)
    x_2 = np.ones(10)
    y = np.ones(10)*2

    tags = [[{'a': x}, {'b': x}, {'c': x}],
            [{'a': y}, {'b': x}, {'c': x_2}]]

    tags_relevant = _select_relevant_tags(tags)
    assert tags_relevant == [[{'a': x}], [{'a': y}]]


def test_select_relevant_tags_pandas():
    pd = pytest.importorskip('pandas')

    x = pd.DataFrame([{'a': 2, 'b': 3}])
    x_2 = pd.DataFrame([{'a': 2, 'b': 3}])
    y = pd.DataFrame([{'a': 2, 'b': 1}])

    tags = [[{'a': x}, {'b': x}, {'c': x}],
            [{'a': y}, {'b': x}, {'c': x_2}]]

    tags_relevant = _select_relevant_tags(tags)
    assert tags_relevant == [[{'a': x}], [{'a': y}]]


# Equality tests


@pytest.mark.parametrize('x', [True, False])
def test_eval_bool_as_bool(x):
    res = _eval_as_bool(x)
    assert isinstance(res, bool)
    assert res is x


def test_eval_as_bool_numpy_array():
    np = pytest.importorskip('numpy')
    x = np.ones((10, 10))
    y = np.ones((10, 10))
    res = _eval_as_bool(x == y)
    assert isinstance(res, bool)
    assert res is True


@pytest.mark.filterwarnings('ignore:Comparing sparse matrices', 'ignore:something_else')
def test_eval_as_bool_scipy_sparse():
    sp = pytest.importorskip('scipy.sparse')
    np = pytest.importorskip('numpy')

    x = sp.csr_matrix(np.ones((10, 10)))
    y = sp.csr_matrix(np.ones((10, 10)))
    res = _eval_as_bool(x == y)
    assert isinstance(res, bool)
    assert res is True


def test_eval_as_bool_pandas_frame():
    pd = pytest.importorskip('pandas')
    x = pd.DataFrame([{'a': 2, 'b': 2}])
    y = pd.DataFrame([{'a': 2, 'b': 2.}])
    res = _eval_as_bool(x == y)
    assert isinstance(res, bool)
    assert res is True


def test_eval_as_bool_pandas_series():
    pd = pytest.importorskip('pandas')
    x = pd.Series({'a': 2, 'b': 2})
    y = pd.Series({'a': 2, 'b': 2.})
    res = _eval_as_bool(x == y)
    assert isinstance(res, bool)
    assert res
