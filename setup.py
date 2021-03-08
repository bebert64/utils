# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="utils_by_db",
    version="1.1",
    author="Don Beberto",
    author_email="bebert64@gmail.com",
    description="Various utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    package_data={"utils": ["py.typed"]},
    packages=setuptools.find_packages(include=["utils", "utils.*"]),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License",
        "Operating System :: Windows",
    ],
    python_requires=">=3.8",
)
