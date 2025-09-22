#!/usr/bin/env python3
"""
Setup script for Linux Armoury - ASUS ROG Laptop Control GUI
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="linux-armoury",
    version="1.0.0",
    author="th3cavalry",
    description="GUI application for ASUS ROG laptop control on Linux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/th3cavalry/Linux-Armoury",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Hardware",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PySide6>=6.4.0",
        "psutil>=5.9.0",
    ],
    entry_points={
        "console_scripts": [
            "linux-armoury=linux_armoury.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "linux_armoury": ["assets/*", "ui/*"],
    },
)