from zaf.component.decorator import component, requires
from zaf.messages.message import EndpointId

from k2.sut.log import sut_add_log_source
from sutevents import LOG_LINE_RECEIVED

LOG_LINE_GENERATOR_ENDPOINT = EndpointId('log-line-generator', '')


@requires(messagebus='MessageBus')
@requires(sut='Sut')
@requires(config='Config')
@component(scope='session')
class LogLineGenerator(object):

    def __init__(self, messagebus, sut, config):
        self._messagebus = messagebus
        self._sut = sut
        self._log_entity = 'loglinegenerator-{sut}'.format(sut=self._sut)
        self._config = config

    def __call__(self, line):
        self._messagebus.trigger_event(
            LOG_LINE_RECEIVED, LOG_LINE_GENERATOR_ENDPOINT, entity=self._log_entity, data=line)

    def __enter__(self):
        config = {}
        sut_add_log_source(config, self._sut.entity, self._log_entity)
        self._config.update_config(config, -1, 'LogLineGenerator')
        self._messagebus.define_endpoints_and_messages(
            {
                LOG_LINE_GENERATOR_ENDPOINT: [LOG_LINE_RECEIVED]
            })
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


@requires(log_line_generator=LogLineGenerator)
@requires(sut_events='SutEvents')
def test_matching_log_line(log_line_generator, sut_events):

    with sut_events.wait_for_log_line('matching') as lines:
        log_line_generator('matching')
        assert lines.get(timeout=1).string == 'matching'


@requires(log_line_generator=LogLineGenerator)
@requires(sut_events='SutEvents')
def test_not_matching_log_line(log_line_generator, sut_events):

    with sut_events.wait_for_log_line('not matching') as lines:
        log_line_generator('matching')
        lines.get(timeout=0)
