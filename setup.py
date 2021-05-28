#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

requirements = []

setup_requirements = []

test_requirements = []

setup(
    author="Haimasree Bhattacharya",
    author_email="haimasree.de@gmail.com",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="Python Boilerplate contains all the \
        boilerplate you need to create a Python package.",
    entry_points={
        "console_scripts": [
            "kipoi_veff2=kipoi_veff2.cli:score_variants",
            "merge=kipoi_veff2.merge:merge",
        ],
    },
    install_requires=requirements,
    license="MIT license",
    include_package_data=True,
    keywords="kipoi_veff2",
    name="kipoi_veff2",
    packages=find_packages(include=["kipoi_veff2", "kipoi_veff2.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/kipoi/kipoi_veff2",
    version="0.1.0",
    zip_safe=False,
)
