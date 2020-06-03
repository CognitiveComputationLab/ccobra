.. _myfirstmodel:

My First Model
==============

This tutorial will walk you through the creation of a model for CCOBRA.

Overview of CCOBRA models
-------------------------

CCOBRA provides an interface class called `CCobraModel` which defines
the set of function used to handle the framework-model communication:

========================= ======== =====================================================================================
Function name             Required Description
========================= ======== =====================================================================================
``setup_environment``     no       Provide meta-information about the evaluation setting.
``start_participant``     no       Provide information about the participant to be predicted for.
``end_participant``       no       Callback hook for when evaluation for a participant ends.
``pre_train``             no       Provides data for training on unrelated examples.
``pre_train_person``      no       Provides data for training on responses by the participant to be predicted for.
``pre_person_background`` no       Provides data for training on external data from the participant to be predicted for.
``predict``               yes      Queries the model for a prediction for a specific task.
``adapt``                 no       Provides the true participant response to allow for online learning.
========================= ======== =====================================================================================

Lifetime
::::::::

The evaluation paradigm of CCOBRA fundamentally relies on the comparison of
predictions with the true responses given by individual participants. As a
result models are queried individually for each task a human participant
provided a response for. In some circumstances (e.g., when leave-one-out
crossvalidation is performed), the responses given by all remaining participants
is used as training data for the model.

To ensure that no responses provided as part of the training dataset leak into
the respective participant evaluations, CCOBRA clearly defines the lifespan of a
model to only last for a single participant. Technically, this means that after
all predictions for a participant have been obtained, a new instance of the model
is created to provide a clean starting point for the evaluation of the next
participant.

For model developers, this means that no clean-up or reset steps are required.
Models can be developed in the mindset that they will only be applied to predict
responses for a single participant.

Implementing my first model
---------------------------

Pre-Training
::::::::::::

Predictions
:::::::::::

Adaptions
:::::::::
