""" Model importer implementation. Used for dynamically importing model classes
for automated evaluation.

Copyright 2018 Cognitive Computation Lab
University of Freiburg
Nicolas Riesterer <riestern@tf.uni-freiburg.de>

"""

import importlib
import inspect
import os
import sys

from .. import CCobraModel

class ModelImporter(object):
    """ Model importer class. Supports dynamical importing of modules,
    detection of model classes, and instantiation of said classes.

    """

    def get_class(self, model_path, superclass=CCobraModel):
        python_files = []
        abs_path = os.path.abspath(model_path)
        if os.path.isfile(abs_path):
            python_files.append(abs_path)
        else:
            python_files = [
                os.path.join(abs_path, f) for f in os.listdir(
                    abs_path) if os.path.isfile(
                        os.path.join(abs_path, f)) and f[-2:] == "py"]

        candidates = {}
        candidate_class_names = set()

        for python_file in python_files:
            module_name = os.path.splitext(os.path.basename(python_file))[0]

            module = importlib.machinery.SourceFileLoader(
                module_name, python_file).load_module(module_name)

            member_class_modules = inspect.getmembers(module, inspect.isclass)

            candidate_module = None
            candidate_class = None
            for member_class_module in member_class_modules:
                member_class = member_class_module[1]

                if member_class is superclass:
                    continue
                elif issubclass(member_class, superclass):
                    if candidate_module:
                        raise ValueError(
                        'Multiple model classes found in file ' \
                        '(e.g., {} and {}). ' \
                        'Please only specify one per file.'.format(
                            member_class.__name__, candidate_class.__name__))
                    candidate_module = module
                    candidate_class = member_class

            if candidate_module:
                full_name = '{}.{}'.format(
                    candidate_module.__name__, candidate_class.__name__)
                candidates[full_name] = (candidate_module, candidate_class)
                candidate_class_names.add(full_name)

        if len(candidates) == 0:
            raise ValueError(
                "No suitable classes found in model_path '{}'.".format(
                    model_path))
        if len(candidates) == 1:
            return list(candidates.values())[0][1]

        remaining_classes = set([x[1] for x in candidates.values()])
        for full_name, content in candidates.items():
            candidate_module = content[0]
            candidate_class = content[1]
            imported_modules = inspect.getmembers(
                candidate_module, inspect.ismodule)

            for imported_module in imported_modules:
                imported_module = imported_module[1]

                for other in candidates:
                    other_module = candidates[other][0]
                    other_class = candidates[other][1]

                    if str(other_module) == str(imported_module):
                        remaining_classes.remove(other_class)

        if len(remaining_classes) > 1:
            raise ValueError(
                "Could not determine main class. Candidates were: '{}'.".format(
                    remaining_classes))
        elif len(remaining_classes) == 1:
            return list(remaining_classes)[0]
        else:
            raise ValueError("Could not determine main class.")

    def __init__(self, model_path, superclass=object):
        """ Imports a model based on a given python source script. Dynamically
        identifies the contained model class and prepares for instantiation.

        Parameters
        ----------
        model_path : str
            Path to the python script to import. May be absolute or relative.

        superclass : object, optional
            Superclass determining which classes to consider for
            initialization.

        Raises
        ------
        ValueError
            When multiple applicable model classes are found (determined via
            the superclass parameter). Only one single model is allowed per
            file.

        ValueError
            When no model with the given superclass is found.

        """

        self.old_modules = set(sys.modules)
        self.class_attribute = self.get_class(model_path, superclass)

    def unimport(self):
        """ Cuts off all dependencies loaded together with the module from
        the module graph.

        Attention: Might cause problems with garbage collection.

        """

        # Make sure that modules with same names do not produce conflicts
        loaded_modules = set(sys.modules) - self.old_modules
        for module_name in loaded_modules:
            if module_name.startswith('torch'):
                continue
            del sys.modules[module_name]

    def instantiate(self, model_kwargs):
        """ Creates an instance of the imported model by calling the empy
        default constructor.

        """

        return self.class_attribute(**model_kwargs)
