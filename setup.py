import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='CCOBRA',
    description='Core functionality and class interfaces of ORCA.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='0.1',
    packages=['ccobra'],
    license='MIT',
    author='Nicolas Riesterer, Daniel Brand, Lukas Elflein',
    author_email='riestern@tf.uni-freiburg.de, daniel.brand@cognition.uni-freiburg.de, elfleinl@tf.uni-freiburg.de',
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
