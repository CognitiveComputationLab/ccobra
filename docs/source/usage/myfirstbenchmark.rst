.. _myfirstbenchmark:

My First Benchmark
==================

Overview
--------

A CCOBRA benchmark is a JSON file which specifies the information required by CCOBRA to perform
a model evaluation. Benchmark files consist of the following attributes:

============================== ======== =====================================================================================================================================================
Attribute                      Required Description
============================== ======== =====================================================================================================================================================
``type``                       yes      Evaluation type out of [``prediction``, ``coverage``, ``loo-coverage``, ``adaption``].
``data.test``                  yes      Evaluation data.
``data.pre_train``             no       Population pre-training data (fed to ``pre_train`` function).
``data.pre_train_person``      no       Personal pre-training data (fed to ``pre_train_person`` function). Contains data from the same domain and experiment as test.
``data.pre_person_background`` no       Personal background training data (fed to ``pre_person_background`` function). Contains data from other domains as test.
``corresponding_data``         no       Flag to indicate that participant identifiers are consistent across datasets.
``domains``                    no       List of domains contained in the data.
``response_types``             no       List of response types contained in the data.
``models``                     yes      List of models to evaluate.
``task_encoders``              no       Dictionary mapping from domains to task encoder classes to abbreviate task representations for the result output.
``response_encoders``          no       Dictionary mapping from domains to response encoder classes to abbreviate response representations for the result output.
``comparator``                 no       Class providing a function for assigning a score to a given prediction with respect to the true response (pre-defined: `equality`, `absdiff`, `nvc`).
``aux_evaluations``            no       List of additional evaluation settings using auxiliary data columns as targets (e.g., reaction times in addition to responses)
============================== ======== =====================================================================================================================================================

Benchmark Types
:::::::::::::::

The benchmark type determines what information the model is provided with before making the prediction.
Since the selection of the right type can be crucial, it is described in detail 
:ref:`on this page <benchmarktypes>`.

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

Auxiliary Evaluations
:::::::::::::::::::::

In addition to the prediction of responses, CCOBRA allows the inclusion of auxiliary evaluations
based on different columns in the dataset. Each of these auxiliary evaluations is represented as
a dictionary containing the following keys:

- ``data_column``: Column in the dataset to use as prediction targets.
- ``comparator``: See table above or the respective section below.
- ``task_encoders``: See table above.
- ``response_encoders``: See table above.
- ``prediction_fn_name``: Name of the function to use for generating predictions (must be contained in the model).
- ``adaption_fn_name``: Name of the function to use for adaption.

Suppose a syllogistic dataset contains the additional `rt` column representing reaction times. Given a model
that implements the `predict_rt(...)` and `adapt_rt(...)` functions for predicting and adapting to
reaction times, respectively, the auxiliary evaluation can be specified as follows:

.. code-block:: json

    {
        "aux_evaluations": [{
            "data_column": "rt",
            "comparator": "absdiff",
            "task_encoders": {
                "syllogistic": "%ccobra%/syllogistic/task_encoder_syl.py"
            },
            "response_encoders": {
                "syllogistic": "%ccobra%/syllogistic/resp_encoder_syl.py"
            },
            "prediction_fn_name": "predict_rt",
            "adaption_fn_name": "adapt_rt"
        }]
    }

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
        ]
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

Comparators
-----------

Comparators are functions used in the CCOBRA evaluation to quantify the correctness or error of a prediction.
There are four build-in comparators that can be referenced directly:

Equality
::::::::

The equality comparator is the default comparator. For everything besides multiple-choice evaluations,
it returns 1 if the prediction and the true response are exactly equal, and 0 otherwise. For multiple-choice,
it represents both, prediction and true response, as a binary vector (with length according to the number of choices).
The returned value is then the mean absolute error (MAE) between those vectors.

It can be used in the benchmark specification by using adding ``"comparator": "equality"``.

Absolute Difference
:::::::::::::::::::

This comparator is suited for comparing number values and calculates the absolute difference.
The CCOBRA evaluation thereby shows the MAE. For example, it is good for predicting ratings or response times.

It can be used in the benchmark specification by using adding ``"comparator": "absdiff"``.

Squared Difference
:::::::::::::::::::

This comparator is suited for comparing number values and calculates the squared difference.
The CCOBRA evaluation thereby shows the mean squared error MSE. 

It can be used in the benchmark specification by using adding ``"comparator": "squareddiff"``.

No Valid Conclusion
:::::::::::::::::::

This is a special comparator that is suited only for single-choice tasks where no valid conclusion (NVC) is a possible response.
In syllogistic reasoning, NVC plays a special role as the correct answer to most tasks, therefore it can be used to assess the 
performance of models to handle exactly this response.

It can be used in the benchmark specification by using adding ``"comparator": "nvc"``.

Custom Comparators
::::::::::::::::::

You can create your own comparators using a custom class implementing :autolink:`ccobra.CCobraComparator`.
To use your class in the benchmark file, simply reference the respective path to the python file:
``"comparator": "path/to/custom_comparator.py"``.

Custom Task/Response-Encoders
:::::::::::::::::::::::::::::

In similar fashion, you can use own task- or response-encoders, by writing custom classes that implement
:autolink:`ccobra.CCobraTaskEncoder` or :autolink:`ccobra.CCobraResponseEncoder` and reference them in the
benchmark specification. For example by adding

.. code-block:: json

    "task_encoders": {
        "mydomain": "path/to/custom/my_task_encoder.py"
    }

you would add a task encoder for a domain called `mydomain`.

.. note:: A task encoder and response encoder is required to obtain the most-frequent answer table in the CCOBRA output.
    Since contents of tasks can vary, it is important for CCOBRA to know which tasks should be aggregated.

Running the Benchmark
---------------------

The evaluation specified by the benchmark file can be performed by CCOBRA by executing the
following command (assuming the JSON file is called ``baseline-adaption.json``):

.. code::

    $> ccobra path/to/benchmark/folder/baseline-adaption.json

More information about running CCOBRA can be found on the page :ref:`runningccobra`.
