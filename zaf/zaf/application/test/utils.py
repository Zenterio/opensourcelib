"""
module description.

extended module description
"""
import inspect

from zaf.application.context import ApplicationContext
from zaf.commands.command import CommandId
from zaf.component.decorator import Requirement
from zaf.component.manager import ComponentInfo
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.config.types import Path
from zaf.extensions.extension import AbstractExtension, CommandExtension, FrameworkExtension
from zaf.messages.message import EndpointId, MessageId


class Comp1Class(object):

    def method(self):
        """Do stuff."""


def comp2_function():
    pass


comp1 = ComponentInfo(
    name='comp1',
    callable_name='call1',
    doc='comp1 description\n\ncomp1 extended description',
    module=__name__,
    default_scope_name=None,
    cans=['can_a', 'can_b'],
    requires=[Requirement(arg='compA', args=None, scope='session', can=['can_a'])],
    extension='ext1',
    methods=[
        function for _, function in inspect.getmembers(Comp1Class, predicate=inspect.isfunction)
    ],
    callable=Comp1Class,
    priority=1)

comp2 = ComponentInfo(
    name='comp2',
    callable_name='comp2',
    doc='comp2 description\n\ncomp2 extended description',
    module=__name__,
    default_scope_name='module',
    cans=['can_b', 'can_c'],
    requires=[
        Requirement(
            arg='compB', args=['arg1'], instance=False, scope='test', can=['can_b', 'can_c'])
    ],
    extension='ext2',
    methods=[],
    callable=comp2_function,
    priority=0)

all_components = [comp2, comp1]

bools = ConfigOptionId(
    'bools',
    'bool description\n\nbool extended description',
    option_type=bool,
    default=[True],
    multiple=True,
    hidden=True)
entity = ConfigOptionId(
    'entity',
    'entity description\n\nentity extended description',
    multiple=True,
    entity=True,
    namespace='ns')
path = ConfigOptionId(
    'path',
    'path description\n\npath extended description',
    option_type=Path(exists=False),
    default=None,
    multiple=True,
    at=entity)
all_contexts = ConfigOptionId(
    'all.contexts',
    'Included in all application contexts',
    hidden=True,
)
extendable_context = ConfigOptionId(
    'extendable.context',
    'Included in extendable application context',
    application_contexts=ApplicationContext.EXTENDABLE)
internal_context = ConfigOptionId(
    'internal.context',
    'Included in internal application context',
    application_contexts=ApplicationContext.INTERNAL)

m1 = MessageId('m1', 'm1 description\n\nm1 extended description\n')
m2 = MessageId('m2', 'm2 description\n\nm2 extended description')
m3 = MessageId('m3', 'm3 description\ncontinues')

e1 = EndpointId('e1', 'e1 description')
e2 = EndpointId('e2', 'e1 description\ncontinues\n\ne1 extended description\n')

c1 = CommandId(
    'c1', 'c1 description\n\nc1 extended description\n', lambda a: None,
    [ConfigOption(bools, required=True),
     ConfigOption(extendable_context, required=True)])
c2 = CommandId(
    'c2',
    'c2 description\nc2 description continue\n\nc2 extended description\n',
    lambda a: None, [ConfigOption(path, required=True),
                     ConfigOption(entity, required=False)],
    hidden=True)
c3 = CommandId(
    'c3',
    'c3 description\nc3 description continue\n\nc3 extended description\n',
    lambda a: None, [],
    parent=c2,
    application_contexts=ApplicationContext.EXTENDABLE)


@FrameworkExtension(
    name='ext1',
    config_options=[ConfigOption(path, required=True)],
    commands=[c2, c1],
    endpoints_and_messages={
        e1: [m3, m1],
    },
    groups=['group'])
class Ext1(AbstractExtension):
    """
    ext1 description.

    ext1 extended description
    """
    pass


Ext1.namespace = 'namespace1'


@CommandExtension(
    name='ext2',
    config_options=[
        ConfigOption(bools, required=False),
        ConfigOption(entity, required=True, instantiate_on=True)
    ],
    extends=['c1'],
    endpoints_and_messages={e2: [m3, m2]},
    groups=['group'])
class Ext2(AbstractExtension):
    pass


Ext2.namespace = 'namespace1'


@FrameworkExtension(
    name='ext3',
    config_options=[
        ConfigOption(all_contexts, required=True),
        ConfigOption(extendable_context, required=True),
        ConfigOption(internal_context, required=True),
    ],
    commands=[c3])
class Ext3(AbstractExtension):
    """
    ext1 description.

    ext1 extended description
    """
    pass


Ext3.namespace = 'namespace2'

all_extensions = [Ext3, Ext2, Ext1]
