.. _runningccobra:

Running CCOBRA
==============

A benchmark file can be run with CCOBRA using the following command:

.. code:: none

    $> cd <path_to_benchmark>
    $> ccobra benchmark.json

Once all models are evaluated, HTML code is created to bundle the results into a dashboard.
The corresponding HTML code is written to a file next to the benchmark JSON following the 
format ``<benchmark-json-name>_<timestamp>.html``. Within that HTML page, there is an overview of the results, 
the possibility to save the dataset with the model prediction, and the model parameters (if available).

In some development environments, it can be useful to start CCOBRA via a python script, instead of the ``ccobra`` executable.
For these cases, it is possible to run the benchmarks by executing the ``run_ccobra.py`` script in the root folder:

.. code:: none

    $> cd <path_to_repository>/
    $> python run_ccobra.py <path_to_benchmark/benchmark.json>

Even though the majority of the time, CCOBRA will be simply run directly on a benchmark, there are some additional options to make it more convenient.
CCOBRA supports several arguments that allow to adjust the way the evaluation is executed. The arguments can be passed to ccobra after the benchmark-file.

* ``--version``: Prints the current version.
* ``--help``: Shows an overview over the argument options.
* ``--output OUTPUT``: Defines the way CCOBRA creates the output where OUTPUT is one of the following:

    * ``browser``: The HTML output is generated and directly displayed in the default browser, once CCOBRA finishes (default). 
    * ``server``: The HTML output generated in the console (stdout), so that it can be used as a server response. Any other output is omitted.
    * ``file``: The HTML output is only generated, but not opened.
    * ``none``: The HTML output is not generated. Instead, ``--save`` and ``--modellog`` need to be used.
* ``--save SAVE``: Saves the CSV file containing the model predictions to each task directly to the path provided in SAVE.
* ``--modellog MODELLOG``: Saves the JSON file containing the model parameters directly to the path provided in MODELLOG.
* ``--model MODEL``: Adds an additional model to the benchmark. MODEL thereby is the path to the CCOBRA model file. This is useful when comparing an own model to other models in an existing benchmark.
* ``--classname CLASSNAME``: In case several classes are within the provided model-file, the class to be benchmarked can be specified here.
* ``--cache CACHE``: Allows to specify a cache (the CSV of a previous run), so that results don't have to be computed again.
* ``--logginglevel LOGGINGLEVEL``: Sets the logging level of CCOBRA. Must be one of [NONE, DEBUG, INFO, WARNING].

For example, the following command would run CCOBRA so that it does not generate an HTML file, but stores the benchmark results directly:

.. code:: none

    $> cd <path_to_repository>/benchmarks/syllogistic
    $> ccobra baseline-adaption.json --output none --save "results.csv"


