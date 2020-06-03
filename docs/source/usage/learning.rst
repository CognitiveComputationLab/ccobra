.. _learning:

Learning in CCOBRA
==================

CCOBRA is fundamentally based on the idea that models need to account for all
cognitive information processing systems. For that matter, the evaluation
scheme defined by CCOBRA's model interface relies on two distinct phases:
global pre-training and individual adaptation. The following paragraphs
introduce these learning phases.

Modeling Problem
----------------

At the core of CCOBRA lies the problem of generating predictions for individual
human reasoners. This problem is composed of the following algorithmic
components:

- **Input**: Reasoning task such as a single syllogism ("All A are B; All B
  are C; What follows?").
- **Output**: Generated prediction to the given task. In contrast to common
  statistical or data scientific analyses, the focus is not on predicting a
  distribution, but on generating a single response (e.g., "All A are C").
- **Scope**: In the end, CCOBRA models are not models for aggregated data
  accounting for a population of reasoners, but predictors for a specific
  individual.

.. note:: Models for the CCOBRA framework should be written with one specific
  individual in mind. The benchmark will handle model initialization and
  separation of individuals for the prediction and adaption phases by itself.

Phases of Learning
------------------

Since CCOBRA's model interaction comprises two types of learning, it strays
away from regular machine learning and pattern recognition problems where
modeling is usually constrained to a single learning and a subsequent model
application phase where parameters stay fixed. The following sections should
give additional insight into the high-level ideas surrounding pre-training and
adaption.

A Metaphor for CCOBRA's Learning
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To understand the learning procedure of CCOBRA, it is useful to consider an
example. Let's assume that there is a video platform which intends to provide
its users with content suggestions they are likely to enjoy (``predict``).

If a new user creates an account the platform has no idea about the individual
preferences but is still supposed to give useful suggestions. One way to
acquire information about useful initial guesses is by considering the
preferences of the population. By learning which content most other users
enjoy, it becomes possible to identify trends which may also be of interest to
unknown users (``pre_train``).

In some cases the system can utilize information about the new user that is
available from other sources. For example, the user might link his account to
an existing social-media account, which allows the system to retrieve some
background information about the user, e.g., tags used by the user or videos
that were liked by user. This information can be utilized to create an initial
user profile (``pre_person_background``).

By interacting with the user and learning about which suggestions are
aligned, a user profile is constructed which contains individual preferences
and distinguishing features (``adapt``). The more the user interacts with the
platform, the more knowledge can it amass. This information can then be
integrated into the suggestion generation algorithm to provide suggestions
ever increasing in quality.

Finally, assume that the video platform started without a system to recommend
content and the user was already using the platform. In this case, the old 
interactions have to be taken into account as well (``pre_train_person``). 
This case is similar to the adaption, with the difference that the information 
is not presented one at a time, but as a batch of interactions instead. By 
default, CCOBRA implements ``pre_train_person`` by calling ``adapt`` for each 
recorded interaction of the user.

Pre-Training: Global Effects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Model pre-training in CCOBRA has the goal to leverage given information about
the problem domain (training dataset) in order to extract an initial
parameterization. This should allow for a sensible warm-start of the model and
serve as the basis for fine-grained tuning to the individual. Pre-training is
only performed in the beginning, once per participant. After the model is
pre-trained, the predict-adapt-cycle begins.

Pre-Training: Person Background
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

CCOBRA can provide models with background information about a participant. 
This information is not part of the problem domain, but consist of behavioral
data of the particpant in other domains. Models can utilize this information
to adjust their initial parameterization.

Pre-Training: Person
~~~~~~~~~~~~~~~~~~~~

In some scenarios, the warm-start of models should be improved even further.
CCOBRA offers the possiblity to pass parts of the data to be predicted in
advance. This way, models are given the opportunity to adjust their 
parameterization to the specific participant before the the predict-adapt-cycle
begins.

Adaption: Individual Effects / User Profile
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Adaption is the actual *training* of the model. It immediately follows a
predict-call and contains the task information as well as the true response of
the individual being modeled. It should be used to infer information about the
specific reasoning processes of the individual being models. Adapt is called
once per task, directly following the corresponding prediction.

.. note:: The benchmark specification decides wether or not the adaption and 
  pre-training options mentioned above are available. Models for the CCOBRA 
  framework should be written to utilize but not expect the additional 
  information.