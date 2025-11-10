"""Módulo de configuração do pacote estatab."""

from setuptools import setup, find_namespace_packages

__version__ = '0.1.0'
__author__ = 'Murilo Couto de Oliveira'
__email__ = 'murilo.couto-oliveira@usp.br'

setup(
    name='estatab',
    version=__version__,
    url='https://github.com/mcoutolive/estatab',
    packages=find_namespace_packages(include=['estatab', 'estatab.*'], where='src'),
    include_package_data=True,
    install_requires=[
        'pytest>=7.3.0',
        'joblib',
        'pytest-cov',
        'pytest-mock',
        'pytest-randomly'],
    entry_points={
        'console_scripts': [],
    },
    author=__author__
)
