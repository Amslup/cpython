"""Object-oriented filesystem paths.

This module provides classes to represent abstract paths and concrete
paths with operations that have semantics appropriate for different
operating systems.
"""

from pathlib._abc import *
from pathlib._local import *

__all__ = (_abc.__all__ +
           _local.__all__)
