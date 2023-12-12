#!/usr/bin/env python3

from setuptools import setup

setup(
    name="tinylogdir",
    version="0.1.1",
    description="A lightweight library for creating output directories of python scripts.",
    author="Florian Fervers",
    author_email="florian.fervers@gmail.com",
    packages=["tinylogdir"],
    install_requires=[
        "pyyaml",
    ],
    license="MIT",
    zip_safe=False,
    url="https://github.com/fferflo/tinylogdir",
)
