""" Model importer implementation. Used for dynamically importing model classes
for automated evaluation.

Copyright 2018 Cognitive Computation Lab
University of Freiburg
Nicolas Riesterer <riestern@tf.uni-freiburg.de>

"""

import importlib
import inspect
import os
import ccobra

class ModelImporter(object):
    """ Model importer class. Supports dynamical importing of modules,
    detection of model classes, and instantiation of said classes.

    """

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

        self.module_name = os.path.splitext(os.path.basename(model_path))[0]

        # Scan module for the model class
        imported_module = importlib.import_module(self.module_name)

        self.class_attribute = None
        for i in dir(imported_module):
            attribute = getattr(imported_module, i)

            if inspect.isclass(attribute) and issubclass(attribute, superclass):
                # important to allow 'from superclass_module import superclass'
                if attribute is superclass:
                    continue
                if self.class_attribute:
                    raise ValueError(
                        'Multiple model classes found (e.g., {} and {}). ' \
                        'Please only specify one per file.'.format(
                            self.class_attribute, attribute))
                self.class_attribute = attribute

        if not self.class_attribute:
            raise ValueError('No model subclassing {} found.'.format(superclass))

    def instantiate(self):
        """ Creates an instance of the imported model by calling the empy
        default constructor.

        """

        return self.class_attribute()
