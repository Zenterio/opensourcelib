from zaf.component.decorator import requires


@requires(zk2='Zk2')
def test_dummy_default_value(zk2):
    result = zk2(
        ['powermeter', 'dummypowermeter'],
        'powermeter --suts-ids box --suts-box@powermeter dummy',
        wait=True)
    assert '4.2 W' in result.stdout


@requires(zk2='Zk2')
def test_dummy_custom_value(zk2):
    result = zk2(
        ['powermeter', 'dummypowermeter'],
        'powermeter --suts-ids box --suts-box@powermeter dummy '
        '--suts-box@dummypowermeter-value 0.42',
        wait=True)
    assert '0.42 W' in result.stdout
