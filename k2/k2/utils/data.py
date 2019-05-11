from collections import OrderedDict


class DataDefinition(object):
    """Data container which preserve the data member order."""

    def __init__(self, attributes, default=None):
        """
        Create a new DataDefinition.

        :param attributes List of strings with the name of data attributes (initialized to None)
                          or
                          OrderedDict where keys becomes attributes and values
                          pre-initilized data.
        :param default    default value for all attributes when attributes is a list.
                          Has no use when passing OrderedDict.

        attribute name can not be '_attributes', due to name collision.
        """
        error_msg = 'Attribute can not be named _attributes due to name collision.'

        if isinstance(attributes, (list, tuple)):
            self._attributes = attributes
            for m in attributes:
                if m == '_attributes':
                    raise AttributeError(error_msg)
                setattr(self, m, default)
        elif isinstance(attributes, (OrderedDict)):
            self._attributes = attributes.keys()
            for k, v in attributes.items():
                if k == '_attributes':
                    raise AttributeError(error_msg)
                setattr(self, k, v)
        else:
            raise TypeError('attributes argument must be a list, tuple or OrderedDict')

    def get_data(self):
        """
        Return an ordered dictionary with the attributes and values.

        The order is specied by the attributes definition passed in the contructor.
        """
        data = OrderedDict()
        for attribute in self._attributes:
            data[attribute] = getattr(self, attribute)
        return data
