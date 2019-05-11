"""Classes and functions related to constructing rule configuration objects."""

import re
from collections import OrderedDict

import munch
from validate_email import validate_email


def dict_to_raw_config(dict_tree):
    return munch.munchify(dict_tree)


def merge_configs(*configs):
    result = munch.munchify({})
    for cfg in reversed(configs):
        result.update(cfg)
    return result


class RawConfigParser():

    def __init__(self, config_check=False):
        self.errors = OrderedDict()
        self.config_check = config_check

    def parse_raw_root(self, root):
        root, root_errors = self.check_attributes('root', root, _root_attributes)
        if root_errors is not None:
            self.add_error('root', root_errors)
            return root

        definitions = []
        for definition in map(self.parse_raw_definition, root.definitions):
            definitions.append(definition)
        self.check_duplicate_definition_ids(definitions)
        root.definitions = definitions
        return root

    def parse_raw_definition(self, raw_definition):
        definition, definitionError = self.check_attributes(
            'item definition', raw_definition, _definition_attributes)
        if definitionError is not None:
            self.add_error(str(definition), definitionError)
            return None

        definition.markers = self.parse_raw_markers(definition.markers, definition.samples)
        definition.invalidators = self.parse_raw_markers(
            definition.invalidators, definition.samples)
        definition.watchers = self.parse_raw_emails(definition.watchers)
        return definition

    def parse_raw_markers(self, raw_markers, samples):
        markers = []
        for raw_marker in raw_markers:
            try:
                marker = self.parse_raw_marker(raw_marker)
                markers.append(marker)
                if self.config_check:
                    for sample in samples:
                        match = marker.search(sample)
                        if match is not None:
                            break
                    else:
                        raise ParseMarkerErrorInfo(raw_marker, Exception('Missing sample for'))

            except Exception as e:
                self.add_error(raw_marker, e)
        return markers

    def parse_raw_marker(self, raw_marker):
        try:
            return re.compile(raw_marker)
        except Exception as e:
            raise ParseMarkerErrorInfo(raw_marker, e)

    def parse_raw_emails(self, raw_emails):
        emails = []
        for email in raw_emails:
            try:
                if not validate_email(email):
                    raise ParseEmailErrorInfo(email, Exception('Invalid email address'))
                else:
                    emails.append(email)
            except Exception as e:
                self.add_error(email, e)
        return emails

    def check_attributes(self, config_name, config_obj, attribute_definitions):
        attr_error = AttributeErrorInfo(config_name, config_obj)
        for def_attr in attribute_definitions:
            attr = def_attr.name
            if attr in config_obj:
                if not self.check_config_value_type(def_attr.value_type, config_obj[attr]):
                    attr_error.add_invalid_value_type_attribute_error(attr)
            else:
                if def_attr.required:
                    attr_error.add_required_attribute_error(attr)
                else:
                    config_obj[attr] = def_attr.default_value

        for attr in sorted(config_obj.keys()):
            if attr not in (a.name for a in attribute_definitions):
                attr_error.add_invalid_attribute_error(attr)

        if attr_error.has_errors():
            return config_obj, attr_error
        else:
            return config_obj, None

    def check_config_value_type(self, config_type, config_obj):
        try:
            return isinstance(config_obj, config_type)
        except TypeError:
            return False

    def check_duplicate_definition_ids(self, definitions):
        seen_ids = set()
        for definition in definitions:
            if hasattr(definition, 'id'):
                if definition.id in seen_ids:
                    msg = 'Multiple definitions share the ID "{id}"'.format(id=definition.id)
                    error = ConfigError(msg)
                    self.add_error(str(definition), error)
                else:
                    seen_ids.add(definition.id)

    def add_error(self, error_id, error):
        self.errors[error_id] = error

    def get_errors(self):
        return self.errors

    def clear_errors(self):
        self.errors.clear()


class ConfigError(Exception):

    def __init__(self, msg, original_exception=None):
        super().__init__(type(self))
        self.msg = msg
        self.original_exception = original_exception

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg


class ParseMarkerErrorInfo(ConfigError):

    def __init__(self, marker, error):
        super().__init__(str(error), error)
        self.marker = marker
        self.error = error
        self.contexts = []

    def add_context(self, index, data):
        self.contexts.append(ConfigSourceContext(index, data))

    def __eq__(self, other):
        if other is None:
            return False
        return self.marker == other.marker and self.contexts == other.contexts

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        result = "{err}: '{marker}'\n".format(err=self.error, marker=self.marker)
        result += '\n'.join((str(cxt) for cxt in self.contexts))
        result += '\n'
        return result

    def __unicode__(self):
        return self.__str__()


class ParseEmailErrorInfo(ConfigError):

    def __init__(self, email, error):
        self.email = email
        self.error = error
        self.contexts = []

    def add_context(self, index, data):
        self.contexts.append(ConfigSourceContext(index, data))

    def __eq__(self, other):
        if other is None:
            return False
        return self.email == other.email and self.contexts == other.contexts

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        result = "{err}: '{email}'\n".format(err=self.error, email=self.email)
        result += '\n'.join((str(cxt) for cxt in self.contexts))
        result += '\n'
        return result

    def __unicode__(self):
        return self.__str__()


class ConfigSourceContext():

    def __init__(self, index, data):
        self.index = index
        self.data = data

    def __eq__(self, other):
        if other is None:
            return False
        return self.index == other.index and self.data == other.data

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '{index}:{data}'.format(index=self.index, data=self.data)

    def __unicode__(self):
        return self.__str__()


class AttributeErrorInfo():

    REQUIRED_ATTRIBUTE = 'Missing required attribute'
    INVALID_ATTRIBUTE = 'Invalid attribute'
    INVALID_VALUE_TYPE = 'Invalid value type for attribute'

    MAX_LINES = 25

    def __init__(self, config_type, config_object):
        self.config_type = config_type
        self.config_object = config_object
        self.contexts = []
        self.max_lines = self.MAX_LINES

    def add_required_attribute_error(self, attribute):
        self.add_attribute_error(attribute, self.REQUIRED_ATTRIBUTE)

    def add_invalid_attribute_error(self, attribute):
        self.add_attribute_error(attribute, self.INVALID_ATTRIBUTE)

    def add_invalid_value_type_attribute_error(self, attribute):
        self.add_attribute_error(attribute, self.INVALID_VALUE_TYPE)

    def add_attribute_error(self, attribute, error):
        self.contexts.append(AttributeErrorContext(attribute, error))

    def __eq__(self, other):
        if other is None:
            return False
        return self.config_type == other.config_type and \
            self.config_object == other.config_object and \
            self.contexts == other.contexts

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        objstr = self.config_object.toYAML()
        lines = objstr.split('\n')
        if len(lines) > self.max_lines:
            lines = lines[:self.max_lines]
            lines.append('...')
            objstr = '\n'.join(lines)
        result = "{conf_type}:\n'{conf_obj}'\n".format(conf_type=self.config_type, conf_obj=objstr)
        result += '\n'.join((str(cxt) for cxt in self.contexts))
        return result

    def __unicode__(self):
        return self.__str__()

    def has_errors(self):
        return bool(len(self.contexts))


class AttributeErrorContext():

    def __init__(self, attribute, error):
        self.attribute = attribute
        self.error = error

    def __eq__(self, other):
        if other is None:
            return False
        return self.attribute == other.attribute and self.error == other.error

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "{err}: '{attribute}'\n".format(err=self.error, attribute=self.attribute)

    def __unicode__(self):
        return self.__str__()


class ConfigAttributeDefinition():

    def __init__(self, name, value_type, default_value, required):
        self.name = name
        self.value_type = value_type
        self.default_value = default_value
        self.required = required


_definition_attributes = [
    ConfigAttributeDefinition('title', str, '', True),
    ConfigAttributeDefinition('id', str, '', True),
    ConfigAttributeDefinition('desc', str, '', True),
    ConfigAttributeDefinition('markers', list, [], True),
    ConfigAttributeDefinition('invalidators', list, [], False),
    ConfigAttributeDefinition('samples', list, [], False),
    ConfigAttributeDefinition('watchers', list, [], False),
]
_root_attributes = [ConfigAttributeDefinition('definitions', list, [], True)]
