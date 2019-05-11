import os
import re

from zaf.component.decorator import component, requires

SEQ = 'sequential'
CON = 'concurrent'
CALL = 'callback'

EVENT = 'event'
REQUEST = 'request'

NO = 'no_component'
ONE = 'one_component'
TRANS = 'transitive_components'


@component
@requires(metrics='CreateSingleValueMetric')
@requires(zk2='Zk2')
class BenchmarkEventBus(object):

    def __init__(self, zk2, metrics):
        self.zk2 = zk2
        self.metrics = metrics

    def __call__(
            self, number_of_messages, number_of_dispatchers, dispatcher_type, message_type,
            handler_type):
        result = self.zk2(
            ['measureeventsandrequests', 'runcommand'],
            '--log-level off '
            'run '
            '--number-of-messages {number_of_messages} '
            '--dispatcher-type {dispatcher_type} '
            '--number-of-dispatchers {number_of_dispatchers} '
            '--message-type {message_type} '
            '--handler-type {handler_type} '.format(
                number_of_messages=number_of_messages,
                number_of_dispatchers=number_of_dispatchers,
                dispatcher_type=dispatcher_type,
                message_type=message_type,
                handler_type=handler_type,
            ),
            file_logging=False,
            plugin_path=os.path.join('systest', 'data', 'plugins'))
        m = re.search(r'time: ([0-9]+)', result.stdout)

        handler_type_ext = '_{handler_type}'.format(
            handler_type=handler_type) if handler_type != 'no_component' else ''
        dispatcher_count_pre = '{number_of_dispatchers}_'.format(number_of_dispatchers=number_of_dispatchers) if \
            number_of_dispatchers != 1 else ''

        namespace = (
            'trigger_{number_of_messages}_{message_type}s'.format(
                number_of_messages=number_of_messages, message_type=message_type) if
            number_of_messages != 1 else 'trigger_{message_type}'.format(message_type=message_type))

        measurement = '{dispatcher_count_pre}{dispatcher_type}_dispatcher{dispatcher_plural}{handler_type_ext}'.format(
            dispatcher_count_pre=dispatcher_count_pre,
            dispatcher_type=dispatcher_type,
            dispatcher_plural='s' if number_of_dispatchers > 1 else '',
            handler_type_ext=handler_type_ext,
        )

        self.metrics('.'.join(['benchmark', namespace, measurement]), int(m.group(1)))


@requires(benchmark='BenchmarkEventBus')
def test_measure_1600_events_with_sequential_dispatcher(benchmark):
    benchmark(1600, 1, SEQ, EVENT, NO)


@requires(benchmark='BenchmarkEventBus')
def test_measure_40_events_with_40_sequential_dispatchers(benchmark):
    benchmark(40, 40, SEQ, EVENT, NO)


@requires(benchmark='BenchmarkEventBus')
def test_measure_event_with_1600_sequential_dispatcher(benchmark):
    benchmark(1, 1600, SEQ, EVENT, NO)


@requires(benchmark='BenchmarkEventBus')
def test_measure_1600_events_with_concurrent_dispatcher(benchmark):
    benchmark(1600, 1, CON, EVENT, NO)


@requires(benchmark='BenchmarkEventBus')
def test_measure_40_events_with_40_concurrent_dispatchers(benchmark):
    benchmark(40, 40, CON, EVENT, NO)


@requires(benchmark='BenchmarkEventBus')
def test_measure_event_with_1600_concurrent_dispatcher(benchmark):
    benchmark(1, 1600, CON, EVENT, NO)


@requires(benchmark='BenchmarkEventBus')
def test_measure_1600_events_with_callback_dispatcher(benchmark):
    benchmark(1600, 1, CALL, EVENT, NO)


@requires(benchmark='BenchmarkEventBus')
def test_measure_40_events_with_40_callback_dispatchers(benchmark):
    benchmark(40, 40, CALL, EVENT, NO)


@requires(benchmark='BenchmarkEventBus')
def test_measure_event_with_1600_callback_dispatcher(benchmark):
    benchmark(1, 1600, CALL, EVENT, NO)


@requires(benchmark='BenchmarkEventBus')
def test_measure_1600_requests_with_sequential_dispatcher(benchmark):
    benchmark(1600, 1, SEQ, REQUEST, NO)


@requires(benchmark='BenchmarkEventBus')
def test_measure_40_requests_with_40_sequential_dispatchers(benchmark):
    benchmark(40, 40, SEQ, REQUEST, NO)


@requires(benchmark='BenchmarkEventBus')
def test_measure_request_with_1600_sequential_dispatcher(benchmark):
    benchmark(1, 1600, SEQ, REQUEST, NO)


@requires(benchmark='BenchmarkEventBus')
def test_measure_1600_requests_with_concurrent_dispatcher(benchmark):
    benchmark(1600, 1, CON, REQUEST, NO)


@requires(benchmark='BenchmarkEventBus')
def test_measure_40_requests_with_40_concurrent_dispatchers(benchmark):
    benchmark(40, 40, CON, REQUEST, NO)


@requires(benchmark='BenchmarkEventBus')
def test_measure_request_with_1600_concurrent_dispatcher(benchmark):
    benchmark(1, 1600, CON, REQUEST, NO)


@requires(benchmark='BenchmarkEventBus')
def test_measure_1600_requests_with_callback_dispatcher(benchmark):
    benchmark(1600, 1, CALL, REQUEST, NO)


@requires(benchmark='BenchmarkEventBus')
def test_measure_40_requests_with_40_callback_dispatchers(benchmark):
    benchmark(40, 40, CALL, REQUEST, NO)


@requires(benchmark='BenchmarkEventBus')
def test_measure_request_with_1600_callback_dispatcher(benchmark):
    benchmark(1, 1600, CALL, REQUEST, NO)


@requires(benchmark='BenchmarkEventBus')
def test_measure_1600_events_with_sequential_dispatcher_with_one_component(benchmark):
    benchmark(1600, 1, SEQ, EVENT, ONE)


@requires(benchmark='BenchmarkEventBus')
def test_measure_40_events_with_40_sequential_dispatchers_with_one_component(benchmark):
    benchmark(40, 40, SEQ, EVENT, ONE)


@requires(benchmark='BenchmarkEventBus')
def test_measure_event_with_1600_sequential_dispatcher_with_one_component(benchmark):
    benchmark(1, 1600, SEQ, EVENT, ONE)


@requires(benchmark='BenchmarkEventBus')
def test_measure_1600_events_with_concurrent_dispatcher_with_one_component(benchmark):
    benchmark(1600, 1, CON, EVENT, ONE)


@requires(benchmark='BenchmarkEventBus')
def test_measure_40_events_with_40_concurrent_dispatchers_with_one_component(benchmark):
    benchmark(40, 40, CON, EVENT, ONE)


@requires(benchmark='BenchmarkEventBus')
def test_measure_event_with_1600_concurrent_dispatcher_with_one_component(benchmark):
    benchmark(1, 1600, CON, EVENT, ONE)


@requires(benchmark='BenchmarkEventBus')
def test_measure_1600_events_with_callback_dispatcher_with_one_component(benchmark):
    benchmark(1600, 1, CALL, EVENT, ONE)


@requires(benchmark='BenchmarkEventBus')
def test_measure_40_events_with_40_callback_dispatchers_with_one_component(benchmark):
    benchmark(40, 40, CALL, EVENT, ONE)


@requires(benchmark='BenchmarkEventBus')
def test_measure_event_with_1600_callback_dispatcher_with_one_component(benchmark):
    benchmark(1, 1600, CALL, EVENT, ONE)


@requires(benchmark='BenchmarkEventBus')
def test_measure_1600_requests_with_sequential_dispatcher_with_one_component(benchmark):
    benchmark(1600, 1, SEQ, REQUEST, ONE)


@requires(benchmark='BenchmarkEventBus')
def test_measure_40_requests_with_40_sequential_dispatchers_with_one_component(benchmark):
    benchmark(40, 40, SEQ, REQUEST, ONE)


@requires(benchmark='BenchmarkEventBus')
def test_measure_request_with_1600_sequential_dispatcher_with_one_component(benchmark):
    benchmark(1, 1600, SEQ, REQUEST, ONE)


@requires(benchmark='BenchmarkEventBus')
def test_measure_1600_requests_with_concurrent_dispatcher_with_one_component(benchmark):
    benchmark(1600, 1, CON, REQUEST, ONE)


@requires(benchmark='BenchmarkEventBus')
def test_measure_40_requests_with_40_concurrent_dispatchers_with_one_component(benchmark):
    benchmark(40, 40, CON, REQUEST, ONE)


@requires(benchmark='BenchmarkEventBus')
def test_measure_request_with_1600_concurrent_dispatcher_with_one_component(benchmark):
    benchmark(1, 1600, CON, REQUEST, ONE)


@requires(benchmark='BenchmarkEventBus')
def test_measure_1600_requests_with_callback_dispatcher_with_one_component(benchmark):
    benchmark(1600, 1, CALL, REQUEST, ONE)


@requires(benchmark='BenchmarkEventBus')
def test_measure_40_requests_with_40_callback_dispatchers_with_one_component(benchmark):
    benchmark(40, 40, CALL, REQUEST, ONE)


@requires(benchmark='BenchmarkEventBus')
def test_measure_request_with_1600_callback_dispatcher_with_one_component(benchmark):
    benchmark(1, 1600, CALL, REQUEST, ONE)


@requires(benchmark='BenchmarkEventBus')
def test_measure_1600_events_with_sequential_dispatcher_with_transitive_component(benchmark):
    benchmark(1600, 1, SEQ, EVENT, TRANS)


@requires(benchmark='BenchmarkEventBus')
def test_measure_40_events_with_40_sequential_dispatchers_with_transitive_component(benchmark):
    benchmark(40, 40, SEQ, EVENT, TRANS)


@requires(benchmark='BenchmarkEventBus')
def test_measure_event_with_1600_sequential_dispatcher_with_transitive_component(benchmark):
    benchmark(1, 1600, SEQ, EVENT, TRANS)


@requires(benchmark='BenchmarkEventBus')
def test_measure_1600_events_with_concurrent_dispatcher_with_transitive_component(benchmark):
    benchmark(1600, 1, CON, EVENT, TRANS)


@requires(benchmark='BenchmarkEventBus')
def test_measure_40_events_with_40_concurrent_dispatchers_with_transitive_component(benchmark):
    benchmark(40, 40, CON, EVENT, TRANS)


@requires(benchmark='BenchmarkEventBus')
def test_measure_event_with_1600_concurrent_dispatcher_with_transitive_component(benchmark):
    benchmark(1, 1600, CON, EVENT, TRANS)


@requires(benchmark='BenchmarkEventBus')
def test_measure_1600_events_with_callback_dispatcher_with_transitive_component(benchmark):
    benchmark(1600, 1, CALL, EVENT, TRANS)


@requires(benchmark='BenchmarkEventBus')
def test_measure_40_events_with_40_callback_dispatchers_with_transitive_component(benchmark):
    benchmark(40, 40, CALL, EVENT, TRANS)


@requires(benchmark='BenchmarkEventBus')
def test_measure_event_with_1600_callback_dispatcher_with_transitive_component(benchmark):
    benchmark(1, 1600, CALL, EVENT, TRANS)


@requires(benchmark='BenchmarkEventBus')
def test_measure_1600_requests_with_sequential_dispatcher_with_transitive_component(benchmark):
    benchmark(1600, 1, SEQ, REQUEST, TRANS)


@requires(benchmark='BenchmarkEventBus')
def test_measure_40_requests_with_40_sequential_dispatchers_with_transitive_component(benchmark):
    benchmark(40, 40, SEQ, REQUEST, TRANS)


@requires(benchmark='BenchmarkEventBus')
def test_measure_request_with_1600_sequential_dispatcher_with_transitive_component(benchmark):
    benchmark(1, 1600, SEQ, REQUEST, TRANS)


@requires(benchmark='BenchmarkEventBus')
def test_measure_1600_requests_with_concurrent_dispatcher_with_transitive_component(benchmark):
    benchmark(1600, 1, CON, REQUEST, TRANS)


@requires(benchmark='BenchmarkEventBus')
def test_measure_40_requests_with_40_concurrent_dispatchers_with_transitive_component(benchmark):
    benchmark(40, 40, CON, REQUEST, TRANS)


@requires(benchmark='BenchmarkEventBus')
def test_measure_request_with_1600_concurrent_dispatcher_with_transitive_component(benchmark):
    benchmark(1, 1600, CON, REQUEST, TRANS)


@requires(benchmark='BenchmarkEventBus')
def test_measure_1600_requests_with_callback_dispatcher_with_transitive_component(benchmark):
    benchmark(1600, 1, CALL, REQUEST, TRANS)


@requires(benchmark='BenchmarkEventBus')
def test_measure_40_requests_with_40_callback_dispatchers_with_transitive_component(benchmark):
    benchmark(40, 40, CALL, REQUEST, TRANS)


@requires(benchmark='BenchmarkEventBus')
def test_measure_request_with_1600_callback_dispatcher_with_transitive_component(benchmark):
    benchmark(1, 1600, CALL, REQUEST, TRANS)
