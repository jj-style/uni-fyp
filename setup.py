import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="rdpgen",
    version="0.0.1",
    description="Recursive Descent Parser Generator - University Final Year Project",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/jj-style/uni-fyp",
    author="JJ Style",
    author_email="style.jj@protonmail.com",
    license="GNU General Public License v3 (GPLv3)",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=["rdpgen"],
    include_package_data=True,
    install_requires=["jinja2", "click", "toml", "tomli", "regex", "case-convert"],
    entry_points={
        "console_scripts": [
            "rdpgen=rdpgen.cli:cli",
        ]
    },
)
