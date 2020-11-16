""" CCOBRA benchmark functionality.

.. rubric:: Submodules

.. autosummary::
   :toctree: _autosummary

   ccobra.benchmark.comparators

.. rubric:: Functions

.. autofunction:: dir_context
.. autofunction:: entry_point
.. autofunction:: fix_model_path
.. autofunction:: fix_rel_path
.. autofunction:: main
.. autofunction:: parse_arguments
.. autofunction:: silence_stdout

.. rubric:: Classes

.. autoclass:: Benchmark
    :members:
.. autoclass:: ModelInfo
    :members:
.. autoclass:: Evaluator
    :members:
.. autoclass:: ModelImporter
    :members:

"""

from . import comparators

from .benchmark import Benchmark, ModelInfo, fix_rel_path, fix_model_path
from .contextmanager import dir_context
from .evaluator import Evaluator
from .modelimporter import ModelImporter
from .runner import entry_point, parse_arguments, main, silence_stdout
from .evaluation_handler import EvaluationHandler
