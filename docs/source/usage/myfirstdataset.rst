.. _myfirstdataset:

My First Dataset
================

This tutorial covers the typical process for integrating a novel dataset
into the CCOBRA framework. This is necessary if you want to apply CCOBRA
models to your own datasets.

Overview
--------

Base format
^^^^^^^^^^^

The goal of the dataset preparation process is the creation of a CSV
dataset file which contains the information required to perform evaluations
using CCOBRA. CCOBRA datasets consist of five required attributes
(i.e., columns in a CSV dataset file): ``id``, ``sequence``, ``domain``,
``task``, ``response_type``, ``choices``, and ``response``. Additionally,
you can specify additional attributes which will be passed to models as
parameters to the respective functions (e.g., ``predict()``). Each line
in the CSV file represents a single task presented to a participant along
with the experimental response given to it.

================= =============== ===============================================
Attribute         Data type       Description
================= =============== ===============================================
``id``            ``int``/``str`` Unique participant identifier.
``sequence``      ``int``         Position in the experimental sequence.
``domain``        ``str``         Task domain.
``task``          ``str``         Task information.
``response_type`` ``str``         Response type information.
``choices``       ``str``         Possible response choices.
``response``      ``str``         Experimental response given by the participant.
================= =============== ===============================================

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

Preparing my first dataset
--------------------------

For this tutorial, we will exemplarily retrace the steps which have been
taken to create the Ragni2016_ dataset for syllogistic reasoning.

Id
^^^^^^^

The ``id`` column represents a unique identifier for participants in the
dataset. It does not matter whether this identifier is a string token
(e.g., *AKU78*) or a numerical identifier.

The Ragni2016_ dataset contains data from 139 participants. Consequently,
numerical identifiers ranging from 1 to 139 were used.

Sequence
^^^^^^^^

The ``sequence`` column represents a number which identifies the position
of a particular task in the experimental sequence. Technically, these numbers
do not need to start at a particular starting value (e.g., 0 or 1). Internally,
CCOBRA sorts the task data for each participant. Sequence identifiers are valid
as long as sorting by them leads to the correct experimental sequence.

The Ragni2016_ dataset was collected as part of an experiment in which each
participant responded to all 64 traditional syllogisms. Consequently, the
sequence columns for all participants contain values from 0 to 63.

Domain
^^^^^^

The ``domain`` column provides information about the domain of the task.
Currently, CCOBRA officially supports the domains ``syllogistic``,
``relational``, and ``propositional`` (cf. the datasets available in the
`repository <https://github.com/CognitiveComputationLab/ccobra/tree/master/benchmarks>`_).
However, CCOBRA is not restricted to the official domains. Internally, the
domain is only used to check whether the models to be evaluated
support the data domains.

The Ragni2016_ dataset contains syllogisms. Hence, the domain is ``syllogistic``.

Task
^^^^

The ``task`` column represents the information about the problem to solve.
To facilitate parsing of multi-premise tasks, CCOBRA supports a task encoding
schema that uses ``/`` to delimit multiple premises presented to the participant.
Additionally, since most of the tasks CCOBRA was developed to support rely on
proposition-based problems, ``;`` can be used to delimit the various propositions
within a premise.

The Ragni2016_ dataset contains traditional syllogistic tasks. A syllogism
consists of two premises containing two terms each (e.g., models, managers,
and clerks):

+--------------------------+----------------------+
| Premises                 | String Encoding      |
+==========================+======================+
| Some models are managers | Some;models;managers |
+--------------------------+----------------------+
| Sll models are clerks    | All;models;clerks    |
+--------------------------+----------------------+

As a result, the full syllogistic problem is represented as
``Some;models;managers/All;models;clerks``.

Response Type
^^^^^^^^^^^^^

The ``response_type`` column provides the information about the type of
response the experiment allowed for. Some experiments allow for a
selection of single or multiple choices out of a set of possibilities.
Others present only a single option and ask for verification. These
differences in study design are captured in the possible values for 
``response_type``:

1. ``single-choice``: A set of possible responses is provided and the
   participant is instructed to select exactly one (e.g., by clicking on
   a button in an internet experiment).
2. ``multiple-choice``: A set of possible responses is provided and the
   participant is instructed to select one or more from them (e.g., by ticking
   boxes next to the possible responses)
3. ``verify``: A single conclusion to a problem is presented and the
   participant is instructed to decide on whether it is valid or invalid
   (e.g., by clicking on buttons labelled true or false). The participant
   is usually instructed to check if the conclusion follows from the
   problem description.
4. ``accept``: A single conclusion to a problem is presented and the
   participant is instructed to decide on whether it is possible or impossible
   (e.g., by clicking on buttons labelled true or false). The difference to
   verification task is that the participant is asked if the conclusion is
   in line (but does not necessarily follow) from the problem description.
5. ``free``: The response does not fit in the other categories (e.g., number
   responses to math problems, percentages or freely typed responses)

In the experiment underlying the Ragni2016_ dataset, the nine possible
conclusion options for syllogistic problems were presented. Subjects had to
select which of the nine possible conclusions followed from the premises.
Accordingly, the response type is ``single-choice``.

Choices
^^^^^^^

The ``choices`` column provides the information about which responses can be
given by participants. In case of single-choice or multiple-choice response
types, choices contains the full set of responses provided to the participants.
In case of verify and accept, the single conclusion to be verified is contained. When using
the free response type, the choices should describe the constraints for the
responses in a meaningful way (e.g., the range of a number).

In similar spirit to the task column, the choices can be encoded as well.
Different unrelated conclusion options are delimited via ``|`` while ``/`` and
``;`` can be used for separating connected pieces of information (e.g., premises)
and propositions, respectively.

In Ragni2016_, the choices column consists of all nine possible conclusion to
the presented syllogism. For the exemplary syllogism presented in the ``task``
section, the choices string is as follows (depicted in multiple lines for reasons
of readability):

.. code:: none

    All;managers;clerks|All;clerks;managers|Some;managers;clerks|
    Some;clerks;managers|Some not;managers;clerks|Some not;clerks;managers|
    No;managers;clerks|No;clerks;managers|NVC

Response
^^^^^^^^

The ``response`` column provides the actual response given by the experimental
participant. In case of verify or accept response types, it is either true or
false to indicate validity and invalidity, respectively. For the other response
types, the column contains the selected conclusion(s) from the set of possible
response options (i.e., the choices column).

Again, the string encoding of the response (as introduced in task and choices)
is used.

In the Ragni2016_ dataset, the response column consists of the single response
selected by a participant. For example, a response to the syllogism presented
above in the section on task, could be ``Some;managers;clerks``.

Additional Information
^^^^^^^^^^^^^^^^^^^^^^

Additional information about tasks (e.g., reaction times) or experimental
participants (e.g., demographic information) can be passed to the models
evaluated in CCOBRA by providing additional columns in the dataset CSV file.
The information of non-required columns is collected and passed as keyword
arguments (``kwargs``) to the ``predict`` function of CCOBRA models.

The Ragni2016_ dataset contains the additional columns ``age`` and ``gender``
indicating the age (numerical) and gender (male or female) of participants.


.. _Ragni2016: https://github.com/CognitiveComputationLab/ccobra/blob/master/benchmarks/syllogistic/data/Ragni2016.csv
