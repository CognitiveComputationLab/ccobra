""" Model import context manager to temporarily switch working directories.

"""

import sys
import os
from contextlib import contextmanager


@contextmanager
def dir_context(path):
    """ Context manager for the working directory. Stores the current working directory before
    switching it. Finally, resets to the old wd.

    Parameters
    ----------
    path : str
        String to set the working directory to.

    """

    context = os.path.abspath(path)
    if os.path.isfile(context):
        context = os.path.dirname(context)

    old_dir = os.getcwd()
    os.chdir(context)
    sys.path.append(context)
    try:
        yield
    finally:
        os.chdir(old_dir)
        sys.path.remove(context)
