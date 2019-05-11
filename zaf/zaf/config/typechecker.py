from zaf.config.types import check_builtin_type


class ConfigOptionIdTypeChecker(object):

    def __init__(self, config):
        self._config = config

    def assert_type(self, option_id, value, entity=None):
        if entity is not None:
            self.type_check_with_entity(option_id, entity, value)
        else:
            option_key = self._config._option_key(option_id)
            self.type_check_multiple_or_single(option_id, value, option_key)

    def type_check_with_entity(self, option_id, entity, value):
        option_key = self._config._option_key(option_id, entity=entity)
        self.type_check_multiple_or_single(option_id, value, option_key)

    def type_check_multiple_or_single(self, option_id, value, option_key):
        if option_id.multiple:
            if isinstance(value, str):
                raise KeyError(
                    "String '{value}' is not a valid value for multiple option '{key}'".format(
                        value=value, key=option_key))

            for val in value:
                self.type_check_single(option_id, val, option_key)
        else:
            self.type_check_single(option_id, value, option_key)

    def type_check_single(self, option_id, value, option_key):
        # Allow values to be None. This will be caught with requires=True in extensions.
        if value is None:
            return

        if not hasattr(option_id.type, 'is_zaf_type'):
            check_builtin_type(value, option_id.type, option_key)
        elif hasattr(option_id.type, 'wants_config') and option_id.type.wants_config is True:
            option_id.type(value, self._config, key=option_key)
        else:
            option_id.type(value, key=option_key)
