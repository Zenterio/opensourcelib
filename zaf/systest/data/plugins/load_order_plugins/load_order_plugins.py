from zaf.extensions.extension import AbstractExtension, ExtensionConfig, FrameworkExtension

for extension_load_order in [22, 21, 23, 25, 24]:

    @FrameworkExtension(name='loadorderplugins', load_order=extension_load_order)
    class LoadOrder(AbstractExtension):

        def get_config(self, config, requested_config_options, requested_command_config_options):
            load_order = self.__class__.load_order
            previous = config._raw_get(str(load_order - 1), default=20)
            print('load order: {order}, previous: {prev}'.format(order=load_order, prev=previous))
            assert previous == load_order - 1
            return ExtensionConfig({str(load_order): load_order}, priority=1)

    globals()['LoadOrder' + str(extension_load_order)] = LoadOrder
