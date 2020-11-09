.. _firststeps:

First Steps
===========

Installing CCOBRA
-----------------

For instructions on how to install CCOBRA, see :ref:`installation`.

Testing the Installation
------------------------

To test your installation of CCOBRA, you can run one of the provided example
benchmarks. For this, download the CCOBRA repository on `Github <https://github.com/CognitiveComputationLab/ccobra>`_ and extract
it to your computer. To evaluate an exemplary syllogistic benchmark, navigate
to the syllogistic benchmark folder, and run the ``ccobra`` executable:

.. code:: none

    $> cd <path_to_repository>/benchmarks/syllogistic
    $> ccobra baseline-adaption.json

As soon as all models are evaluated you should be presented with a evaluation
result overview in form of a website (see usage information for the ``ccobra``
executable for other forms of output):

.. image:: /_static/result.png

The corresponding HTML code is written to a file next to the benchmark JSON following the format ``<benchmark-json-name>_<timestamp>.html``.

How to Proceed
--------------

Since CCOBRA is domain-agnostic, you can easily integrate custom problem
domains just by providing corresponding datasets and models. To integrate
your own domains into CCOBRA, consider the following steps:

1. Prepare your dataset to adhere to the mandatory format (see :ref:`myfirstdataset`).
2. Provide example models you can evaluate your approaches against (see :ref:`myfirstmodel`).
3. Provide a benchmark specification including your dataset and models (see :ref:`myfirstbenchmark`).
4. Check if your evaluation pipeline is working by running CCOBRA on your benchmark file.
5. Develop, extend, and improve your cognitive models.

.. note:: Note, that for most of the domains of behavioral cognitive science research,
    modifying CCOBRA directly will **not** be necessary. The framework builds on
    the essential idea that models are supposed to simulate the cognitive processes
    of humans when confronted with tasks. Consequently, as long as the experimental
    task can be represented in a textual string-based format, the current
    implementation of CCOBRA will be able to handle your domain.
