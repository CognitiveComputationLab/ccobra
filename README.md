# Cognitive COmputation for Behavioral Reasoning Analysis (CCOBRA) Framework

[![](https://img.shields.io/pypi/v/ccobra.svg)](https://pypi.org/pypi/ccobra/)
[![](https://img.shields.io/pypi/pyversions/ccobra.svg)](https://pypi.org/pypi/ccobra/)
[![GitHub license](https://img.shields.io/github/license/CognitiveComputationLab/ccobra.svg)](https://github.com/CognitiveComputationLab/ccobra/blob/master/LICENSE)
[![DOI](https://zenodo.org/badge/144011537.svg)](https://zenodo.org/badge/latestdoi/144011537)

## Installation

### PyPi

CCOBRA is available via `pip`. To install the current version, run the following command:

```
$> pip install ccobra
```

### Development Version

It is also possible to install a development version of CCOBRA. The difference to the standard version is that changes to the local copy of the repository are directly reflected in the module loaded from Python via `import`. To install the develop version, download a local copy of the repository and run the following commands:

```
$> cd /path/to/repository/
$> python setup.py develop [--user]
```

To remove the development version, run the following commands:

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

Custom models can be implemented by defining classes based on `CCobraModel` interfaces. The following snippet contains the skeleton snippet for a simple syllogistic model always returning the `NVC` response:

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


