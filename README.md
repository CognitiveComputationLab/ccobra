# Online Reasoning for Cognition Analysis (ORCA) Framework

## Dependencies

- Python 3
- Numpy

## Installation

ORCA requires you to install the core modules. This is done by running the following commands:

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

Custom models can be implemented by defining classes based on `OrcaModel` interfaces. The following snippet contains the skeleton snippet for a simple syllogistic model always returning the `NVC` response:

```python
from orca import OrcaModelSyl

class MyModel(OrcaModelSyl):
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


