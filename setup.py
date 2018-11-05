import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='ccobra',
    description='The CCOBRA framework.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/CognitiveComputationLab/ccobra',
    version='0.0.4',
    packages=setuptools.find_packages(),
    license='MIT',
    author='Nicolas Riesterer',
    author_email='riestern@tf.uni-freiburg.de',
    install_requires=[
        'numpy',
        'pandas'
    ],
    classifiers=(
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    )
)
