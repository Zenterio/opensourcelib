import logging
import sys


def configure_logging(verbose=False):
    root = logging.getLogger()
    root.setLevel(logging.ERROR)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

    logging.getLogger('requests').setLevel(logging.WARNING)

    if verbose:
        ch.setLevel(logging.DEBUG)
        root.setLevel(logging.DEBUG)
