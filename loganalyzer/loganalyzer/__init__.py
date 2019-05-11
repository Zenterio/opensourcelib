try:
    from .version import __version__
except ImportError:
    __version__ = None
try:
    from .version import __updated__
except ImportError:
    __updated__ = None

__version__ = '0.0.0' if __version__ is None else __version__
__updated__ = '' if __updated__ is None else __updated__
__copyright__ = '  Copyright 2016 Zenterio AB. All rights reserved.'
__license__ = 'Apache 2.0 License'
__license__text__ = """
  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.
"""
__program_name__ = 'z' + __package__
__shortdesc__ = '{name} -- analyzes a log using a set of configurable rules.'.format(
    name=__program_name__)
__description__ = """
  {name} analyzes a log using a set of configurable rules, defined in a
  configuration file, and outputs a report and a summary of the results.""".format(
    name=__program_name__)
__info__ = """
{desc}

{copyright}

{license}
""".format(
    desc=__shortdesc__, copyright=__copyright__, license=__license__text__)

try:
    import munch

    program_info = munch.munchify(
        {
            'name': __program_name__,
            'version': __version__,
            'updated': str(__updated__),
            'copyright': __copyright__,
            'license': __license__,
            'license_text': __license__text__,
            'description': __description__,
            'short_desc': __shortdesc__,
            'info': __info__
        })
except ImportError:
    pass
