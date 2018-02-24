# neurtu, BSD 3 clause license
# Authors: Roman Yurchak


class Delayed(object):
    """Delayed wrapper class

    Parameters
    ----------
    obj : object
      object, function or Class to delay
    func : {str, None}
      name of the object (build-in) attribute to call
    args: args
      positional arguments passed to ``func``
    args: args
      arguments passed to ``func``
    tags: dict
      optional tags for the delayed object
    """
    def __init__(self, obj, func, args=None, kwargs=None, tags=None):
        self.__obj = obj
        self.__func = func
        if args is None:
            args = ()
        self.__args = args
        if kwargs is None:
            kwargs = {}
        self.__kwargs = kwargs
        if tags is None:
            tags = {}
        self.__tags = tags

    def __call__(self, *args, **kwargs):
        return Delayed(self, '__call__', args, kwargs)

    def __getattr__(self, key):
        return Delayed(self, '__getattr__', args=(key,))

    def __getitem__(self, key):
        return Delayed(self, '__getitem__', args=(key,))

    def compute(self):
        """Evaluate the delayed object"""
        if self.__func is None:
            return self.__obj
        else:
            obj = self.__obj.compute()
            args, kwargs = self.__args, self.__kwargs
            if self.__func == '__call__':
                # this could be an __init__ or a __call__
                return obj(*args, **kwargs)
            elif self.__func == '__getattr__':
                return obj.__getattribute__(*args, **kwargs)
            else:
                return getattr(obj, self.__func)(*args, **kwargs)

    def __repr__(self):
        parent_repr = self.__obj.__repr__()

        def _str2str(x):
            if isinstance(x, str) and not x.strip():
                return "'%s'" % x
            else:
                return x

        args_repr = ['%s' % _str2str(val) for val in self.__args]
        kwargs_repr = ['%s=%s' % (key, _str2str(val))
                       for key, val in self.__kwargs.items()]

        args_kwargs_repr = ','.join(args_repr + kwargs_repr)
        args_repr = ','.join(args_repr)
        kwargs_repr = ','.join(kwargs_repr)

        if self.__func is None:
            if self.__tags:
                tags_repr = ', tags=%s' % self.__tags
            else:
                tags_repr = ''
            parent_repr = '<Delayed(%s%s)>' % (parent_repr.replace('<', '')
                                                          .replace('>', ''),
                                               tags_repr)
            return parent_repr
        elif self.__func == '__call__':
            return (parent_repr[:-1] + '(%s)>' % str(args_kwargs_repr))
        elif self.__func == '__getattr__':
            return (parent_repr[:-1] + '.%s>' % args_repr)
        elif self.__func == '__getitem__':
            return (parent_repr[:-1] + '[%s]>' % args_repr)
        else:
            return (parent_repr +
                    ' -> {} args={} kwargs={}'
                    .format(self.__func, args_repr, kwargs_repr))

    def get_tags(self):
        """Get tags passed at init

        Returns
        -------
        tags : dict
          a dictionary of tags
        """
        if self.__func is None:
            return self.__tags
        else:
            # recursively find the root Delayed object
            return self.__obj.get_tags()


def _is_delayed(obj):
    """Check that object follows the ``class:neurtu.Delayed`` API
    """
    return (hasattr(obj, 'compute') and hasattr(obj, 'get_tags') and
            callable(obj.compute) and callable(obj.get_tags))


def delayed(obj, tags=None):
    """Delayed object evaluation

    Parameters
    ----------
    obj : object
       object or function to wrap
    tags : dict
       optional tags for the produced delayed object

    Returns
    -------
    result : `class:neurtu.Delayed`
       a delayed object

    Example
    -------

    >>> x = delayed('some string').split(' ')[::-1]
    >>> x
    <Delayed('some string').split(' ')[slice(None, None, -1)]>
    >>> x.compute()
    ['string', 'some']


    Using tags

    >>> x = delayed([2, 3], tags={'a': 0}).sum()
    >>> x.get_tags()
    {'a': 0}

    """
    return Delayed(obj, None, tags=tags)
