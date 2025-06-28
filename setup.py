#!/usr/bin/env python3
"""
Setup script for verilog-python package

This is a Python translation of the verilog-perl library, providing
parsing and utilities for the Verilog Language.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="verilog-python",
    version="1.0.0",
    description="Python implementation of Verilog language utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Verilog-Python Translator",
    author_email="",
    url="https://github.com/your-repo/verilog-python",
    packages=find_packages(),
    package_data={
        "verilog_python": ["*.py"],
    },
    entry_points={
        "console_scripts": [
            "vhier=verilog_python.tools.vhier:main",
            "vppreproc=verilog_python.tools.vppreproc:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "License :: OSI Approved :: Artistic License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies required
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    keywords="verilog systemverilog parser preprocessor netlist eda",
    project_urls={
        "Bug Reports": "https://github.com/your-repo/verilog-python/issues",
        "Source": "https://github.com/your-repo/verilog-python",
        "Documentation": "https://github.com/your-repo/verilog-python#readme",
    },
) 