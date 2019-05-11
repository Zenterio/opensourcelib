import logging
import signal

from zaf.component.decorator import requires

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


@requires(app='ZafApp')
def test_abort_signal(app):
    process = app(command='sleep', wait=False)
    process.wait_for_match_in_stdout('starting to sleep', timeout=4)
    process.signal(signal.SIGABRT)
    process.wait_for_match_in_stdout('Handles sig=6', timeout=4)
