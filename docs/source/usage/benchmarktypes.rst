.. _benchmarktypes:

Benchmark Types
===============

CCOBRA offers three types of benchmarks, ``prediction``, ``adaption`` and
``coverage``, where each allows to evaluate different aspects of the
predictive capabilities of a model. 

============== ===================================================================================
Benchmark Type Description
============== ===================================================================================
``prediction`` Only pre-training, models may not adjust during prediction phase.
``adaption``   Pre-training and the possibility to adjust after each prediction.
``coverage``   The full participant data is given to the model before the prediction phase starts.
============== ===================================================================================

Prediction Setting
------------------

In the ``prediction`` setting, CCOBRA provides training data to the models 
before the prediction phase begins. The models are then evaluated on the test
data, without the possibility to re-adjust their parameterization. The setting
can be used to evaluate models developed with population data in mind to models
focussing on individual reasoners. While we strongly encourage to create models
with individual participants in mind, most existing models are still based on
population data. Therefore, it can be important to compare individualized 
models to the existing population-based models. Using the ``prediction``
setting allows this without putting population-based models at an unfair
disadvantage due to their incapability to account for individual data.

Adaption Setting
----------------

in the ``adaption`` setting, CCOBRA provides all available training data to the
models (as in the ``prediction`` setting). Additionally, models are expected to
adjust their parameterization after each prediction. Therefore, CCOBRA calls
the ``adapt`` function of the model after each call of ``predict``, providing
the model with the response that the participant gave to the last task. This
allows models to further adapt to the specific individual reasoner at hand over
time. However, the interpretation of the performance is more complicated as for
the other settings. The performance of a model in this setting does not only
depend on it's ability to represent the respective participant, but also
measures how efficiently it uses the given information.


Coverage Setting
----------------

The ``coverage`` setting is used to evaluate the general ability of a model to
account for individual data. When using this setting, CCOBRA provides models
with the test data of a participant using the ``pre_train_person`` function,
before the respective participant has to be predicted. Therefore, models should
in theory be able to perfectly predict the responses, as they would just need
to replicate the training data. For this reason, models relying on storing the
training data (e.g., the
`MFA model <https://github.com/CognitiveComputationLab/ccobra/blob/master/benchmarks/syllogistic/models/Baseline/MFA-Model/mfa_model.py>`_),
should not be evaluated using this setting. However, as cognitive models
usually only use a small number of meaningful parameters, they might not be
able to represent the participant perfectly in their parameter space. The
results of this setting should thus be interpreted as a measure for the
ability of a model to represent an individual participant.

