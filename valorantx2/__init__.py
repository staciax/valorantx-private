"""
Valorant API Wrapper
~~~~~~~~~~~~~~~~~~~
A basic wrapper for the Valorant API.
:copyright: (c) 2023-present xStacia
:license: MIT, see LICENSE for more details.
"""

__title__ = 'valorantx'
__author__ = 'xStacia'
__license__ = 'MIT'
__copyright__ = 'Copyright 2022-present xStacia'
__version__ = '1.0.0'

from . import utils as utils, valorant_api as valorant_api
from .auth import *
from .client import *
from .enums import *
from .errors import *
from .models import *
