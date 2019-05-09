# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""

import re
from setuptools import setup



version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('private_mount_tool/run.py').read(),
    re.M).group(1)

with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")

setup(
    name = "private-mount-tool",
    packages = ["private_mount_tool"],
    entry_points = {
        "console_scripts": ['private-mount-tool = private_mount_tool.run:main']
        },
    version = version,
    description = "Tool for easily mounting disks to a linux system",
    long_description = long_descr,
    install_requires=[],
    author = "Robert Tisma",
    author_email = "rtisma@gmail.com",
    url = "https://github.com/rtisma/private-mount-tool",
    )
