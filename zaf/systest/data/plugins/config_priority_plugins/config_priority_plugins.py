from zaf.extensions.extension import AbstractExtension, ExtensionConfig, FrameworkExtension


@FrameworkExtension('configpriorityplugins', 21)
class Priority11(AbstractExtension):

    def get_config(self, config, requested_config_options, requested_command_config_options):
        return ExtensionConfig(
            {
                '11': 11,
                '12': 11,
                '13': 11,
                '14': 11,
                '15': 11,
            }, priority=11)


@FrameworkExtension('configpriorityplugins', 24)
class Priority12(AbstractExtension):

    def get_config(self, config, requested_config_options, requested_command_config_options):
        return ExtensionConfig(
            {
                '12': 12,
                '13': 12,
                '14': 12,
                '15': 12,
            }, priority=12)


@FrameworkExtension('configpriorityplugins', 23)
class Priority13(AbstractExtension):

    def get_config(self, config, requested_config_options, requested_command_config_options):
        return ExtensionConfig(
            {
                '13': 13,
                '14': 13,
                '15': 13,
            }, priority=13)


@FrameworkExtension('configpriorityplugins', 25)
class Priority14(AbstractExtension):

    def get_config(self, config, requested_config_options, requested_command_config_options):
        return ExtensionConfig(
            {
                '14': 14,
                '15': 14,
            }, priority=14)


@FrameworkExtension('configpriorityplugins', 22)
class Priority15(AbstractExtension):

    def get_config(self, config, requested_config_options, requested_command_config_options):
        return ExtensionConfig(
            {
                '15': 15,
            }, priority=15)


@FrameworkExtension('configpriorityplugins', 99)
class PrintConfig(AbstractExtension):

    def get_config(self, config, requested_config_options, requested_command_config_options):
        print('11: {prio}'.format(prio=config._raw_get('11')))
        print('12: {prio}'.format(prio=config._raw_get('12')))
        print('13: {prio}'.format(prio=config._raw_get('13')))
        print('14: {prio}'.format(prio=config._raw_get('14')))
        print('15: {prio}'.format(prio=config._raw_get('15')))
        return ExtensionConfig({}, priority=1)
