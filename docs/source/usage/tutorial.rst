.. _tutorial:

Tutorial
========

Installation
------------

Installation instructions can be found in the section on :ref:`installation`.

Introduction to ORCA
--------------------

ORCA's philosophy is based around the fact that models always attempt to solve
specific modeling tasks, either explicitly or implicitly. Contrary to big parts
of the current state of the art in cognitive modeling, ORCA focuses on making
the processes underlying response generation explicit. To this end, ORCA
mandates models to revolve around a single method ``predict(task)`` which asks
for a single prediction in response to a presented ``task``.

In syllogistic reasoning, a toy model might be constructed in a way that it is
always supposed to respond with *No valid response* indicating that no logical
inference can be drawn in response to the given task. Consequently, its
``predict`` method will always return ``NVC``.

The sheer simplicity of ORCA sets it apart from most contemporary modeling
approaches. Models are not required to adhere to rigorous Bayesian fundamentals
nor computational logic calculi nor statistical effects extracted from years
of psychological research. Instead, it encourages tackling core problems of
cognitive science by imposing little to no constraints with respect to the
computational foundation of model instances. The sole requirement is the
ability to make predictions in response to tasks, an arguably trivial
prerequisite.

ORCA heralds the start of a new paradigm of cognitive modeling -- a perspective
that is focused on prediction-based performance. Coupling the goal of achieving
high predictive performance with rich possibilities to infer insight into
the computational principles underlying model implementations, ORCA offers
a modern toolset to aid computer scientists and cognitive scientists alike in
their respective goals.

Structure of the Package
------------------------

The general structure of the ORCA package is to be considered unstable and
non-final due to the relative youth of the project.

Currently, the package contents are structured as followed:

- ``orca``: The root namespace contains base classes and interfaces.
- ``orca.syllogistic``: Syllogistic model interface and data handling routines.

Developing a first Model
------------------------

Implementing models for ORCA is as easy as completing the following template:

.. code-block:: python
    :linenos:

    import orca

    class NVCModel(orca.syllogistic.OrcaModelSyl):
        def __init__(self, name='NVCModel'):
            """ Model constructor.

            Parameters
            ----------
            name : str
                Unique name of the model. Will be used throughout the ORCA
                framework as a means for identifying the model.

            domain : str
                Reasoning domain.

            """

            super(NVCModel, self).__init__(name)
            ...

        def start_participant(self, **kwargs):
            """ Model initialization method. Used to setup the initial state of its
            datastructures, memory, etc.

            """

            ...

        def pre_train(self, dataset):
            """ Pre-trains the model based on one or more datasets.

            Parameters
            ----------
            dataset : :class:`orca.data.orcadata.RawData`
                ORCA raw data container.

            """

            ...

        def predict(self, task, **kwargs):
            """ Predicts weighted responses to a given syllogism.

            Parameters
            ----------
            task : str
                Reasoning task to produce a prediction for.

            Returns
            -------
            ndarray
                Model prediction.

            """

            ...

        def adapt(self, task, target, **kwargs):
            """ Trains the model based on a given task-target combination.

            Parameters
            ----------
            syllogism : str
                Task to produce a response for.

            target : str
                True target answer.

            """

            ...

The goal of this section is to develop a simple toy model in the domain of
syllogistic reasoning that responds with *No Valid Conclusion* to all tasks.
This can be achieved by writing the following lines of code:

.. code-block:: python
    :linenos:

    import orca

    class NVCModel(orca.syllogistic.OrcaModelSyl):
        def __init__(self, name='NVCModel'):
            super(NVCModel, self).__init__(name)

        def predict(self, task, **kwargs):
            return 'NVC'

The ``__init__`` method calls the super constructor providing it with the
model's name which is used for referencing results. Due to its static nature,
``predict`` always returns *No Valid Response*.

The remainder of the functions do not need to be specified.

Evaluating the Model
--------------------

To evaluate the model, a ``.zip`` archive containing the ``model.py`` file can
be uploaded to the `ORCA-Benchmark <http://orca.informatik.uni-freiburg.de/orca_sylwebsite/orca/>`_.

Alternatively, the benchmark script can be downloaded for local usage from its
repository on `Github <https://github.com>`_.
