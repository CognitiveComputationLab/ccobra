.. _myfirstbenchmark:

My First Benchmark
==================

This tutorial walks you through the creation of a benchmark specification file.

Overview
--------

A CCOBRA benchmark is a JSON file which specifies the information required by CCOBRA to perform
a model evaluation. Benchmark files consist of the following attributes:

============================== ======== =============================================================================================================================
Attribute                      Required Description
============================== ======== =============================================================================================================================
``type``                       yes      Evaluation type out of [``prediction``, ``coverage``, ``adaption``].
``data.test``                  yes      Evaluation data.
``data.pre_train``             no       Population pre-training data (fed to ``pre_train`` function).
``data.pre_train_person``      no       Personal pre-training data (fed to ``pre_train_person`` function). Contains data from the same domain and experiment as test.
``data.pre_person_background`` no       Personal background training data (fed to ``pre_person_background`` function). Contains data from other domains as test.
``corresponding_data``         no       Flag to indicate that participant identifiers are consistent across datasets.
``domains``                    no       List of domains contained in the data.
``response_types``             no       List of response types contained in the data.
``models``                     yes      List of models to evaluate.
``domain_encoders``            no       List of domain encoders to abbreviate tasks in the data.
============================== ======== =============================================================================================================================

Path Handling
:::::::::::::

Paths in benchmark specification files can either be provided in an absolute or relative form.
In case of relative paths, CCOBRA interprets them as relative to the location of the benchmark
JSON file.

Some components of the benchmark specification may need reference files within the CCOBRA package.
For instance, if encoders for the officially supported domains (e.g., syllogisms) are required,
the official encoders can be used. To facilitate referencing files within the CCOBRA package,
``%ccobra%`` can be used. It is a shorthand for pointing at the location of the local CCOBRA
installation folder on your machine.

Creation of Benchmark Specification File
----------------------------------------

To illustrate the creation of a benchmark specification file, we retrace the steps taken to create
the ``baseline-adaption.json`` located in the `CCOBRA repository <https://github.com/CognitiveComputationLab/ccobra/blob/master/benchmarks/syllogistic/baseline-adaption.json>`_.

.. code-block:: json

    {
        "type": "adaption",
        "data.test": "data/Ragni2016.csv",
        "data.pre_train": "data/Ragni2016.csv",
        "corresponding_data": true,
        "domains": ["syllogistic"],
        "response_types": ["single-choice"],
        "models": [
            "models/Baseline/Uniform-Model/uniform_model.py",
            "models/Baseline/MFA-Model/mfa_model.py"
        ],
        "domain_encoders": {
            "syllogistic": "%ccobra%/syllogistic/encoder_syl.py"
        }
    }

This benchmark specifies an evaluation of type adaption, i.e., after each prediction has been
retrieved from the model, the true participant response is provided to enable online learning.

As evaluation data, it uses the ``Ragni2016.csv`` dataset. Simultaneously, this dataset is also
used as pre-training data. By setting ``corresponding_data: true``, CCOBRA is instructed to relate
the participant identifiers from the training and test datasets. This causes it to perform a
leave-one-out crossvalidation in which the model for a specific participant receives the data from
all other participants as pre-training data.

The domains and response types of the benchmark are set to ``syllogistic`` and ``single-choice``.

Two models are specified to be considered in the evaluation: The
`uniform model <https://github.com/CognitiveComputationLab/ccobra/blob/master/benchmarks/syllogistic/models/Baseline/Uniform-Model/uniform_model.py>`_
and the
`mfa model <https://github.com/CognitiveComputationLab/ccobra/blob/master/benchmarks/syllogistic/models/Baseline/MFA-Model/mfa_model.py>`_.

Finally, a domain encoder for the syllogistic domain is included to provide encoded forms of the
tasks, predictions, and true participant responses which enable the MFA comparison output.

Running the Benchmark
:::::::::::::::::::::

The evaluation specified by the benchmark file can be performed by CCOBRA by executing the
following command (assuming the JSON file is called ``baseline-adaption.json``):

.. code::

    $> ccobra path/to/benchmark/folder/baseline-adaption.json

CCOBRA generates a HTML file containing visualizations of the evaluation results and opens it
in your system's default browser. The HTML website also offers the possibility to download
the evaluation result data as well as images of the visualizations. The HTML file is automatically
saved in the same folder as the benchmark JSON file.

CCOBRA offers additional command-line arguments which can be displayed by running ``ccobra -h``.
