import threading


class SendSerialCommandData(object):

    def __init__(self, line, timeout):
        self.line = line
        self.event = threading.Event()
        self.timeout = timeout
