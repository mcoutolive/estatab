"""Módulo de configuração do pacote estatab."""

from setuptools import setup, find_namespace_packages

__version__ = '0.1.0'
__author__ = 'Murilo Couto de Oliveira'
__email__ = 'murilo.couto-oliveira@usp.br'

setup(
    name='EstatAB',
    version=__version__,
    url='https://github.com/mcoutolive/estatab',
    packages=find_namespace_packages(
        include=['estatab', 'estatab.*'], where='src'),
    include_package_data=True,
    install_requires=[
        'joblib',
        'numpy==2.3.4',
        'pytest',
        'pytest-cov',
        'pytest-mock',
        'pytest-randomly',
        'scipy==1.16.3',
    ],
    entry_points={
        'console_scripts': [],
    },
    author=__author__
)
