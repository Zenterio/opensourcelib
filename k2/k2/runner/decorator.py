from zaf.component.decorator import Requirement


def disabled(msg):
    """
    Decorate a test case with @disabled to indicate that it should be disabled.

    :param msg: The message to show in test result when the test case is skipped
    """
    if callable(msg):
        raise TypeError('The @disabled decorator may not be used without arguments.')

    def set_disabled(fn):
        fn._k2_disabled = True
        fn._k2_disabled_message = msg
        return fn

    return set_disabled


def foreach(**kwargs):
    """
    Decorate a test case to indicate that it should run once for every matching component or item in list.

    In case it is used for named component matching, the test case will be run once
    for each matched component as a requirement.

    In case it is used with an iterable, the test case will be run once for each
    item in the iterable.

    foreach has the extra parameter `format` which takes a function used to format
    the component/item to convert it to string in a suitable format for reporting.
    The format function defaults to str().
    """

    def decorate(fn):
        fe = ForEach(**kwargs)
        try:
            fn._k2_foreach.insert(0, fe)
        except AttributeError:
            fn._k2_foreach = [fe]
        return fn

    return decorate


class ForEach(Requirement):

    def __init__(self, format=str, **kwargs):
        self.format = format
        kwargs.pop('format', None)
        super().__init__(**kwargs)
