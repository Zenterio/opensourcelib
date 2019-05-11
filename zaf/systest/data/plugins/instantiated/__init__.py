from zaf.config.options import ConfigOptionId

INSTANCES = ConfigOptionId(
    'ids', 'description instance', multiple=True, namespace='instances', entity=True)

DEPENDENT_OPTION = ConfigOptionId('dependent.option', 'description multiple.option', at=INSTANCES)
