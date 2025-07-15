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

In detail, this setting does not call the ``adapt`` method of a model, and does not
populate the ``data.pre_train_person`` field of the benchmark automatically.
When ``data.pre_train`` is provided, models will be pre-trained with it.

.. note:: Depending on the setting of ``corresponding_data``, a leave-one-out
    crossvalidation is still performed. Also, it is important not to use
    ``data.pre_train_person`` in this evaluation. To include information about
    the participants' behavior in other tasks/domains, use 
    ``data.pre_person_background`` instead.


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

LOO-Coverage Setting
--------------------

The ``loo-coverage`` is used to give the models as much information as possible
without giving any model the possibility to simply memorize. Here, the models 
are first provided with the data from ``data.pre_train``. 
Similar to the coverage setting, the ``pre_train_person`` function is then used
to provide models with the individual participant's behavior.

Unlike the coverage setting, models here are given every answer but the one to 
be predicted. This way, models can not memorize the answes and the results are 
fair, even with machine-learning models. However, the models have not only to be
re-trained for each participant, but also for each single task. This makes the
analysis time-consuming.

Which setting should I choose?
------------------------------

The choice of the right evaluation setting is tricky, but there are a few general
purposes for each of them:

In cases where aggregate models are supposed to be tested, ``prediction`` is fitting,
since it is simple and easily interpretable. Also, when aiming at prediction based on
information from other domains, it is a good choice, since no specific fitting is 
necessary. In summary, whenever the models should not be fitted to the data they tested
on at all, ``prediction`` is the right choice.

For assessing what models can theoretically account for, ``coverage`` is the option
to choose. Here, the results clearly show what a model is able to reconstruct given its 
parameter space. It is thereby the best-case for the model. However, in turn, this means
that any proper data-driven model will likely reach 100 percent, since it can simply
memorize the options.

The most complete option is ``loo-coverage``, where each model can perform at the best
conditions without being able to *cheat*: This setting is suited for assessing the 
performance of models without special considerations for their type. Machine learning,
statistical models and cognitive process models can be compared here in absolute terms.
Therefore, it is the right option for analyses of upper bounds, or simply finding the 
truly best performing model.

Finally, ``adaption`` is useful when the focus is about the fitting process itself, too.
Here, it is equally important that models use observations well and adapt quickly.
Additionally, adaption can be used for tasks where participants have multiple interactions:
For example, in a puzzle game, the model could have to successively predict the next move,
but needs to get feedback about the actual move.


