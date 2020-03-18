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

How to Continue
---------------

In the following a couple of standard usage scenarios for working with CCOBRA
are illustrated.

Model Development in Provided Domains
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Model development in CCOBRA essentially boils down to the following steps:

1. Prepare a benchmark specification for your needs by deciding on the
   dataset you want to focus on during development (test and training)
   and the models you want to include to compare your approach against
2. Setup your model for example by copying the content of one of the
   baseline models (e.g., random uniform in syllogistic reasoning)
3. Make sure that your benchmark evaluation pipeline is showing up (do
   all integrated models show up in the produced figures?, etc.)
4. Start developing your approach and continuously test its performance
   against the provided baseline models.

Model Development in Custom Domains
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Since CCOBRA is domain-agnostic, you can easily integrate custom problem
domains just by providing corresponding datasets and models. To integrate
your own domains into CCOBRA, consider the following steps:

1. Prepare your dataset to adhere to the mandatory format (see :ref:`fundamentals`).
   Here, the most crucial step is to decide on a string-based encoding for
   tasks and responses.
2. Provide example models you can evaluate your approaches against (e.g.,
   a random uniform model or a most-frequent answer model).
3. Provide a benchmark specification.
4. Develop and evaluate your approaches.

.. note:: Note, that for most of the domains of behavioral cognitive science research,
    modifying CCOBRA directly will **not** be necessary. The framework builds on
    the essential idea that models are supposed to simulate the cognitive processes
    of humans when confronted with tasks. Consequently, as long as the experimental
    task can be represented in a textual string-based format, the current
    implementation of CCOBRA will be able to handle your domain.
