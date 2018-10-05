# Cognitive COmputation for Behavioral Reasoning Analysis (CCOBRA) Framework

[![](https://img.shields.io/pypi/v/ccobra.svg)](https://pypi.org/pypi/ccobra/)
[![](https://img.shields.io/pypi/pyversions/ccobra.svg)](https://pypi.org/pypi/ccobra/)
[![GitHub license](https://img.shields.io/github/license/CognitiveComputationLab/ccobra.svg)](https://github.com/CognitiveComputationLab/ccobra/blob/master/LICENSE)

## Dependencies

- Python 3
- Numpy
- Pandas

## Installation

CCOBRA requires you to install the core modules. This is done by running the following commands:

```
$> cd /path/to/repository/
$> python setup.py develop|install [--user]
```

#### Uninstallation

```
$> cd /path/to/repository
$> python setup.py develop [--user] --uninstall
```

## First Steps

#### Executing the Examples

Examples for common reasoning domains can be found in `examples/`. To start the example analyses, run the corresponding `start.py` scripts. The following commands run the syllogistic example:

```
$> cd /path/to/repository/examples/syllogism
$> python start.py
```

#### Implementing Custom Models

Custom models can be implemented by defining classes based on `CCOBRAModel` interfaces. The following snippet contains the skeleton snippet for a simple syllogistic model always returning the `NVC` response:

```python
import ccobra

class MyModel(ccobra.syllogistic.SylModel):
    """ Simple static model for syllogistic reasoning always responding with
    NVC.

    """

    def __init__(self, name='MyModel'):
        """ Model constructor. Initializes internal state of the model.

        Parameters
        ----------
        name : str, optional
            Name for the model.

        """

        super(MyModel, self).__init__(name)

    def predict(self, task, **kwargs):
        """ Method for computing predictions of the model.

        Parameters
        ----------
        task : str
            Variable for the syllogism (e.g., AA1).
        kwargs : dict
            Collects additional information from the data

        """

        return 'NVC'
```


