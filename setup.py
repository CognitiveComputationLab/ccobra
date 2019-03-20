import setuptools

import ccobra

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='ccobra',
    description='The CCOBRA framework.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/CognitiveComputationLab/ccobra',
    version=ccobra.__version__,
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    license='MIT',
    author='Nicolas Riesterer',
    author_email='riestern@tf.uni-freiburg.de',
    install_requires=[
        'numpy',
        'pandas'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    entry_points={
        'console_scripts': ['ccobra=ccobra.benchmark.runner:entry_point']
    },
    package_data={
        'ccobra.benchmark.visualization': ['*.js', '*.html', '*.css']
    }
)
