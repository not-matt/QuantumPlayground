#!/usr/bin/env python3

from setuptools import setup


PROJECT_PACKAGE_NAME = "QuantumPlayground"
PROJECT_VERSION = 0.1
PROJECT_LICENSE = "The MIT License"
PROJECT_AUTHOR = "Matthew Bowley"
PROJECT_AUTHOR_EMAIL = "m.bowley98@gmail.com"

INSTALL_REQUIRES = [
    "requests",
    "numpy",
    "matplotlib",
    "jupyter",
    "ipywidgets",
]

setup(
    name=PROJECT_PACKAGE_NAME,
    version=PROJECT_VERSION,
    license=PROJECT_LICENSE,
    author=PROJECT_AUTHOR,
    author_email=PROJECT_AUTHOR_EMAIL,
    install_requires=INSTALL_REQUIRES,
    entry_points={"console_scripts": ["playground = playground.__main__:main"]},
)
