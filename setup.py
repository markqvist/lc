#!/usr/bin/env python3

# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

"""
lc - Humanity's Last Command
A minimal, truly local agentic command executor.
"""

from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as f: long_description = f.read()
exec(open("lc/_version.py", "r").read())

package_data = {
"": [
    "data/README.md",
    "data/GUIDE.md",
    "data/Chrome_Horizons.md",
    ]
}

setup(
    name="lc",
    version=__version__,
    description="Humanity's Last Command - The last command you'll ever need",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Mark Qvist",
    author_email="",
    url="",
    packages=find_packages(),
    package_data=package_data,
    entry_points={
        "console_scripts": [
            "lc=lc.__main__:main",
        ],
    },
    install_requires=[
        "rns>=1.1.3",
        "lxmf>=0.6.0",
        "requests>=2.31",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Shells",
        "Topic :: Utilities",
    ],
    keywords="cli agent ai automation local llm",
    project_urls={
        "Source": "",
        "Tracker": "",
    },
)
