#!/usr/bin/env python3
"""
ChampCom Setup Script
Run: python setup.py install
Or just: python main.py (no install needed)
"""
from setuptools import setup, find_packages

setup(
    name="champcom",
    version="1.0.0",
    description="ChampCom - Operating System Within an Operating System",
    author="thaChamp78",
    packages=find_packages(),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "champcom=main:main",
        ],
    },
)
