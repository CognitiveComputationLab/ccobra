.. _fundamentals:

Fundamentals
============

Datasets
--------

Base format
^^^^^^^^^^^

CCOBRA expects datasets to be specified as comma-separated values (CSV) files.
A minimal dataset contains the set of attributes summarized in the
following table:

============= ================================================================
Attribute     Description
============= ================================================================
id            Unique identifier for experimental participants.
sequence      Index for the position of the task in the experimental sequence.
task          Description of the task to be solved by the participant.
choices       Response options.
response      Response given by the experimental participant.
response_type Type of the response (single-choice, multiple-choice, verify)
domain        Task domain (e.g., syllogistic, propositional, etc.)
============= ================================================================

A crucial aspect for the specification of tasks and responses is their encoding.
Since CCOBRA uses datasets in CSV format, the tasks and responses need to be encoded
in plaintext strings. These strings contain delimiters as follows:

- ``;`` separates terms within a single premise (e.g., "All;A;B" denotes the
  syllogistic premise "All A are B")
- ``/`` separates premises of a task (e.g., "A/iff;A;B" denotes the two premises
  "A" and "A if and only if B")
- ``|`` is used to separate unrelated pieces of information such as different response
  options (e.g., "nothing|B|not;B|not;A|" separates the responses "nothing", "B",
  "not B", and "not A")

The content for the task-specific attributes (task, choices, response) thus
depends largely on the problem domain. Consider an `example from propositional
reasoning <https://github.com/CognitiveComputationLab/ccobra/blob/master/benchmarks/propositional/data/data.csv>`_:

====== ======== ========= ===================== ======== ============= =============
id     sequence task      choices               response response_type domain
====== ======== ========= ===================== ======== ============= =============
...    ...      ...       ...                   ...      ...           ...
WWYIPK 4        A/iff;A;B nothing|B|not;B|not;A B        single-choice propositional
...    ...      ...       ...                   ...      ...           ...
====== ======== ========= ===================== ======== ============= =============

This line represents a response given by participant ``WWYIPK`` given to the fourth
task that was presented in the experimental sequence. The task was ``A/iff;A;B``
which corresponds to the propositional problem

.. code:: none

    A  
    A if and only if B
    ---
    What, if anything, follows?

The set of possible response choices is specified as ``nothing|B|not;B|not;A``
corresponding to the response options

.. code:: none

    No valid conclusion
    B
    not B
    not A

From this set of options, the participant decided to select ``B`` as the conclusion.
Finally, the response type is ``single-choice`` reflecting that only one of the
choices could be selected by the participant and the domain is ``propositional``
reasoning.

Extended Datasets
^^^^^^^^^^^^^^^^^

Some experiments might yield additional data which could be beneficial to
cognitive models. Consider for example introductory questionnaires targeting
demographic information (age, profession, educational background) or psychometric
measures such as personality factors (e.g., Big Five). The additional information
about the individualities of participants enable models to fine-tune their
inferential mechanisms to the participant in question which should allow for
better predictions overall.

In CCOBRA, these additional pieces of information can be appended to the base
format of the CSV dataset as additional columns. Consider an `example for
syllogistic reasoning <https://github.com/CognitiveComputationLab/ccobra/blob/master/benchmarks/syllogistic/data/Ragni2016.csv>`_:

== ======== === ==================== ============= =========== ====== ===
id sequence ... response             response_type domain      gender age
== ======== === ==================== ============= =========== ====== ===
1  0        ... Some;managers;clerks single-choice syllogistic female 56
== ======== === ==================== ============= =========== ====== ===

In this example, the mandatory attributes (see above) are extended by two additional
attributes (``gender``, ``age``) which provide demographic information about the
participant.

Internally, CCOBRA maintains the additional information in dictionaries which
are passed to the relevant model evaluation methods (e.g., ``predict``) as
``kwargs``.

Model Specification
-------------------

Cognitive models in CCOBRA are implemented according to the interface specified
in :class:`ccobra.CCobraModel`. An overview over the different functions is
given in the following table

===================== =======================================================================================================================================
Function              Description
===================== =======================================================================================================================================
start_participant     Hook signaling that the evaluation routine for a specific participant is about to start.
end_participant       Hook signaling that the evaluation routine for a specific participant is about to end.
pre_train             Pre-trains the model using a training dataset unrelated to the participant to be predicted for.
pre_train_person      Personalized training with responses given by the participant to be predicted for.
pre_person_background Personalized training with background information unrelated to the experiment to be predicted for.
predict               Queries the model for a specific prediction.
adapt                 Is called after prediction and provides the true response. Allows the model to fine-tune itself to the participant to be predicted for.
===================== =======================================================================================================================================

The only method models must provide in the CCOBRA framework is `predict`. This
method is supposed to represent the model's inferential mechanism and thus has
to provide a response prediction which can ultimately be used to assess the
model's predictive performance.

Let's consider the `random uniform syllogistic model as an example <https://github.com/CognitiveComputationLab/ccobra/blob/master/benchmarks/syllogistic/models/Baseline/Uniform-Model/uniform_model.py>`_:

.. code:: python

    def predict(self, item, **kwargs):
        return item.choices[np.random.randint(0, len(item.choices))]

This model uses numpy's ``np.random.randint()`` function to draw a random integer
that is then used to select one of the possible response options as its prediction.

Benchmark Specification
-----------------------

After specifying datasets and models to be used in CCOBRA all that is left is to
instruct CCOBRA to perform a specific evaluation. This is handled via JSON
configuration files we call *benchmarks*.

A benchmark can consist of the following information (mandatory ones are in bold
font):

========================== ====================================================================================
Tag                        Description
========================== ====================================================================================
**type**                   Type of the evaluation (prediction, adaption or coverage).
**data.test**              Path to the evaluation dataset.
data.pre_train             Path to the pre training dataset.
data.pre_train_person      Path to the person training dataset.
data.pre_person_background Path to the person background dataset.
corresponding_data         Flag to indicate whether subject ids uniquely identify participants across datasets.
**models**                 List of models to include in the benchmark.
domains                    List of domains relevant for the evaluation.
response_types             List of response types relevant for the evaluation.
domain_encoders            Optional encoders for tasks and responses to allow for prettier output.
========================== ====================================================================================

There are a couple of points to note related to the benchmark specification:

- It no absolute paths are provided, they are interpreted relative to the location of the benchmark JSON file.
- By providing the same datasets to both ``data.test`` and ``data.pre_train`` and setting ``corresponding_data: true``, CCOBRA performs a leave-one-out crossvalidation.

Lets consider an example for syllogistic reasoning:

.. code:: json

    {
        "type": "adaption",
        "data.pre_train": "data/Ragni2016.csv",
        "data.test": "data/Ragni2016.csv",
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

The benchmark instructs CCOBRA to perform an ``adaption`` analysis in which
models are sequentially fed tasks and are updated afterwards. This type of
analysis evaluates the general ability of models to provide accurate predictions
for human behavior. In contrast ``coverage`` would provide all tasks as
person-training data before querying for predictions for the same set of tasks.
This type of analysis essentially evaluates the ability of models to capture
a participant with respect to their parameter spaces (note, that for
database-like models which store training data, this type of analysis does not
provide meaningful results).

Next, training and test datasets are both set to ``Ragni2016.csv`` and
``corresponding_data`` is set to ``true`` indicating that CCOBRA is supposed
to perform leave-one-out crossvalidation in which models are pre-trained by
providing all participants from the data except for the one to be predicted for.

The only important information left is ``models`` in which two baseline models
for syllogistic reasoning, ``uniform_model.py`` (which we have seen above already)
and ``mfa_model.py``, are specified.

After specifying the benchmark, running CCOBRA is as easy as calling the ``ccobra``
executable on it.
