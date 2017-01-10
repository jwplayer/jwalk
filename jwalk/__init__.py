# -*- coding: utf-8 -*-
# flake8: noqa
"""jwalk library.

:copyright: (c) 2017 by JW Player.
:license: Apache 2.0, see LICENSE for more details.
"""
import logging

__title__ = 'jwalk'
__author__ = 'Kamil Sindi, Nir Yungster'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2017 JW Player'
# __version__ = get_version(root='..', relative_to=__file__)

# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())

__all__ = []
from .graph import *

__all__ += graph.__all__

from .corpus import *

__all__ += corpus.__all__

from .skipgram import *

__all__ += skipgram.__all__

from .io import *

__all__ += io.__all__
