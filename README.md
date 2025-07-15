# Cognitive COmputation for Behavioral Reasoning Analysis (CCOBRA) Framework

[![](https://img.shields.io/pypi/v/ccobra.svg)](https://pypi.org/pypi/ccobra/)
[![](https://img.shields.io/pypi/pyversions/ccobra.svg)](https://pypi.org/pypi/ccobra/)
[![GitHub license](https://img.shields.io/github/license/CognitiveComputationLab/ccobra.svg)](https://github.com/CognitiveComputationLab/ccobra/blob/master/LICENSE)
[![DOI](https://zenodo.org/badge/144011537.svg)](https://zenodo.org/badge/latestdoi/144011537)

[[API Documentation]](https://www.pva.tu-chemnitz.de/ccobra/ccobra-doc/)

## Installation

### PyPi

CCOBRA is available via `pip`. To install the current version, run the following command:

```
$> pip install ccobra
```

to update your installation, run `pip install -U ccobra`.

### Development Version

It is also possible to install a development version of CCOBRA. The difference to the standard version is that changes to the local copy of the repository are directly reflected in the module loaded from Python via `import`. To install the develop version, download a local copy of the repository and run the following commands:

```
$> cd /path/to/repository/
$> python -m pip install --editable .
```

### Running CCOBRA

When installed, CCOBRA can be run on a benchmark file:

```
$> cd /path/to/repository/
$> ccobra benchmark.json
```

Alternatively, the runner script `run_ccobra.py` can be run instead:

```
$> cd /path/to/repository/
$> python run_ccobra.py benchmark.json
```
