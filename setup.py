from setuptools import setup, find_packages
from codecs import open
from os import path 

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='nvdocker',
    version='0.0.1',  
    description='nvdocker is library built on top of the docker-py python sdk to build and run docker containers using nvidia-docker.', 
    long_description=long_description, 
    url='https://github.com/acm-uiuc/nvdocker', 
    author='ACM@UIUC',
    author_email='acm@illinois.edu', 
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: University of Illinois/NCSA Open Source License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX :: Linux'
    ],
    keywords='docker nvidia-docker development containers frameworks',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['docker'],
)