"""Contains different configuration readers."""

import argparse
import logging
import os
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from collections import OrderedDict

import yaml
from cchardet import UniversalDetector

from .config import ConfigError, RawConfigParser, dict_to_raw_config

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class YAMLConfigReader():

    def __init__(self, stream, check_config):
        self.stream = stream
        self.errors = OrderedDict()
        self.check_config = check_config
        logger.debug('YAMLConfigReader: created')

    def get_config(self):
        try:
            raw_config = self.get_raw_config()
            parser = RawConfigParser(self.check_config)
            config = parser.parse_raw_root(raw_config)
            logger.debug('YAMLConfigReader: parsed config (config={config})'.format(config=config))
            self.errors = parser.get_errors()
            if len(self.errors) > 0:
                logger.debug('Errors found while parsing: {errors}'.format(errors=self.errors))
                self.identify_errors()
                raise ConfigError(self.get_error_msg())
            return config
        except ConfigError:
            raise
        except AttributeError as e:
            logger.error('YAMLConfigReader: get_config (Attribute error={err})'.format(err=e))
            raise ConfigError(
                'Missing required attribute in configuration (attribute={err})'.format(err=e), e)
        except yaml.error.YAMLError as e:
            logger.error('YAMLConfigReader: get_config (YAML error={err})'.format(err=e))
            raise ConfigError(
                'YAML Error (stream={stream}): {err}'.format(stream=self.stream.name, err=e), e)
        except Exception as e:
            logger.error(
                'YAMLConfigReader: get_config (Unknown error={err}, type={t})'.format(
                    err=e, t=type(e).__name__))
            raise ConfigError('Unknown error while parsing YAML configuration', e)

    def get_raw_config(self):
        return dict_to_raw_config(yaml.load(self.stream))

    def identify_errors(self):
        self.stream.seek(0)
        for index, line in enumerate(self.stream, start=1):
            for marker, err in self.errors.items():
                if marker in line:
                    err.add_context('line {line}'.format(line=index), line.rstrip())
        return self.errors

    def get_error_msg(self):
        msg = 'Configuration parse errors occurred:\n'
        msg += '\n'.join(str(err) for err in self.errors.values())
        return msg


class EnvVarConfigReader():

    PROFILE = 'LOG_ANALYZER_PROFILE'
    DEBUG = 'LOG_ANALYZER_DEBUG'
    ENCODING = 'LOG_ANALYZER_ENCODING'

    def __init__(self, env=os.environ):
        self.env = env
        logger.debug('EnvVarConfigReader: created')

    def get_config(self):
        cfg = {}
        cfg['profile'] = self._parse_bool(self.env.get(self.PROFILE, 'False'))
        cfg['debug'] = self._parse_bool(self.env.get(self.DEBUG, 'False'))
        cfg['encoding'] = self._parse_str(self.env.get(self.ENCODING, None))
        return dict_to_raw_config(cfg)

    def _parse_bool(self, str_value):
        return str_value.lower() not in ('n', 'no', 'f', 'false', '0', '')

    def _parse_str(self, str_value):
        return str_value if not str_value == '' else None


class CmdLineConfigReader():

    def __init__(self, program_info, encoding=None, argv=None):
        self.program_info = program_info
        self.encoding = encoding
        self.argv = argv if argv is not None else sys.argv.copy()
        logger.debug('CmdLineConfigReader: created')

    def detect_encoding(self, path, config):
        """
        Detect the encoding of the file specified by path, unless encoding is already set in config.

        If the autodetection can't determine an
        encoding with confidence, it defaults to UTF-8.

        param path: The path to the input file which encoding should be detected_encoding
        param config: Config object where results are recorded
        """
        config.detected_encoding = None
        config.detected_encoding_confidence = 0

        if config.encoding is not None:
            logger.debug(
                'CmdLineConfigReader: detect_encoding, encoding pre-set'
                ' (encoding={encoding})'.format(encoding=config.encoding))
            return

        default = 'UTF-8'
        detector = UniversalDetector()
        with open(path, 'rb') as file, detector:
            for line in file:
                detector.feed(line)
                if detector.done:
                    break
        confidence = config.detected_encoding_confidence = detector.result['confidence']
        encoding = config.detected_encoding = detector.result['encoding']
        logger.debug(
            'CmdLineConfigReader: detect_encoding '
            '(detected-encoding={encoding}, confidence={confidence})'.format(
                encoding=encoding, confidence=confidence))
        if confidence is not None and float(confidence) >= 0.25 and encoding is not None:
            config.encoding = encoding
        else:
            config.encoding = default
        logger.debug(
            'CmdLineConfigReader: detect_encoding (encoding={encoding})'.format(
                encoding=config.encoding))

    def get_config(self):

        program_version_message = '%(prog)s v{version} ({date})'.format(
            version=self.program_info.version, date=self.program_info.updated)

        parser = ArgumentParser(
            prog=self.program_info.name,
            description=self.program_info.info,
            formatter_class=RawDescriptionHelpFormatter)

        parser.add_argument(
            '-V', '--version', dest='version', action='version', version=program_version_message)

        parser.add_argument(
            dest='configfile',
            type=argparse.FileType('r'),
            help='rule configuration file',
            metavar='CONFIG_FILE')

        parser.add_argument(
            '-i',
            '--in',
            dest='infile',
            default='-',
            help='set log input path [default: stdin (-)]',
            metavar='FILE')

        parser.add_argument(
            '-o',
            '--out',
            dest='outfile',
            default=sys.stdout,
            type=argparse.FileType('w', encoding='UTF-8'),
            help='set report output path [default: stdout (-)]',
            metavar='FILE')

        parser.add_argument(
            '-s',
            '--summary',
            dest='summaryfile',
            default=sys.stdout,
            type=argparse.FileType('w', encoding='UTF-8'),
            help='set summary output path [default: stdout (-)]',
            metavar='FILE')

        parser.add_argument(
            '-v',
            '--verbose',
            dest='verbose',
            action='store_true',
            default=False,
            help='turn on verbose mode [default: %(default)s]')

        parser.add_argument(
            '-q',
            '--quiet',
            dest='quiet',
            action='store_true',
            default=False,
            help='prevent errors from being printed to stderr [default: %(default)s]')

        parser.add_argument(
            '--logfile',
            dest='logfile_path',
            default=None,
            help='set logfile output path [default: %(default)s]',
            metavar='FILE')

        parser.add_argument(
            '--config-check-only',
            dest='config_check',
            action='store_true',
            default=False,
            help='perform config check and exit [default: %(default)s]')

        parser.add_argument(
            '--encoding-check-only',
            dest='encoding_check',
            action='store_true',
            default=False,
            help='perform encoding check of the input file and exit [default: %(default)s]')

        parser.add_argument(
            '--set-encoding',
            dest='encoding',
            default=self.encoding,
            help='Force encoding setting for input file. '
            'If not set, automatic detection of the input file is done.'
            'Encoding settings has no effect when reading from stdin.')

        parser.add_argument(
            '--watchers-file',
            dest='watchers_file',
            default=None,
            type=argparse.FileType('w', encoding='UTF-8'),
            help='Output affected watchers to file',
            metavar='FILE')

        parser.add_argument(
            '--watchers-separator',
            dest='watchers_separator',
            default=', ',
            help='Separator between watchers in the watchers file')

        result = dict_to_raw_config(vars(parser.parse_args(args=self.argv[1:])))

        if result.infile == '-':
            result.infile = sys.stdin
        else:
            if os.path.exists(result.infile):
                self.detect_encoding(result.infile, result)
                result.infile = open(result.infile, 'r', encoding=result.encoding, errors='replace')
            else:
                # Emulate the behavior of other file-based options parsed by the parser.
                msg = "argument -i/--in: can't open '{infile}': [Errno 2] No such file or directory: '{infile}'".format(
                    infile=result.infile)
                logger.error(msg)
                parser.print_usage(sys.stderr)
                sys.stderr.write('zloganalyzer: error: ' + msg + '\n')
                sys.exit(2)

        return result
