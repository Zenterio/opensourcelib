from zaf.component.decorator import requires
from zaf.utils.future import FuturesCollection


@requires(create_series_metric='CreateSeriesMetric')
@requires(create_single_value_metric='CreateSingleValueMetric')
def test_create_some_metrics(create_series_metric, create_single_value_metric):
    futures = create_series_metric('system_memory.used', 199905, timestamp=1)
    futures += create_series_metric('system_memory.used', 5, timestamp=2)
    futures += create_series_metric('system_memory.used', 199901, timestamp=3)
    futures += create_series_metric('system_memory.free', 100, timestamp=1)
    futures += create_series_metric(
        'system_memory.free', 20000, timestamp=2, tags=['zids.bin crashed!'])
    futures += create_series_metric(
        'system_memory.free', 99, timestamp=3, tags=['everything is back to normal'])
    futures += create_single_value_metric('system_memory.total', 200005, timestamp=1)
    futures.wait(timeout=10)


@requires(create_series_metric='CreateSeriesMetric')
def test_create_happy_primes(create_series_metric):
    futures = FuturesCollection()
    for happy_prime in (7, 13, 19, 23, 31, 79, 97, 103, 109, 139, 167, 193, 239, 263, 293, 313, 331,
                        367, 379, 383):
        futures += create_series_metric('happy_primes', happy_prime)
    futures.wait(timeout=10)


@requires(create_series_metric='CreateSeriesMetric')
def test_create_linear_sequences(create_series_metric):
    futures = FuturesCollection()
    for value in range(1, 1000):
        futures += create_series_metric('increasing_series', value, timestamp=value)
    for value in range(1000, 1, -1):
        futures += create_series_metric('decreasing_series', value, timestamp=1001 - value)
    futures.wait(timeout=10)


@requires(create_series_metric='CreateSeriesMetric')
def test_create_metric_series_with_a_single_entry(create_series_metric):
    futures = FuturesCollection()
    futures += create_series_metric('single_entry', 1, timestamp=1000)
    futures.wait(timeout=10)
