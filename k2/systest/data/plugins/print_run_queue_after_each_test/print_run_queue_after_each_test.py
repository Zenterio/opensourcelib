import logging

from zaf.extensions.extension import AbstractExtension, CommandExtension
from zaf.messages.dispatchers import CallbackDispatcher

from k2.cmd.run import RUN_COMMAND
from k2.runner import RUNNER_ENDPOINT, TEST_CASE_FINISHED
from k2.scheduler import GET_CURRENT_RUN_QUEUE

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


@CommandExtension(
    name='printrunqueueaftereachtest',
    extends=[RUN_COMMAND],
)
class PrintRunQueueAfterEachTest(AbstractExtension):

    def register_dispatchers(self, messagebus):
        self._messagebus = messagebus
        self._dispatcher = CallbackDispatcher(messagebus, self.log_run_queue_on_test_case_finished)
        self._dispatcher.register([TEST_CASE_FINISHED], [RUNNER_ENDPOINT])

    def destroy(self):
        self._dispatcher.destroy()

    def log_run_queue_on_test_case_finished(self, message):
        fs = self._messagebus.send_request(GET_CURRENT_RUN_QUEUE)
        print('Run queue: {run_queue}'.format(run_queue=fs[0].result()))
