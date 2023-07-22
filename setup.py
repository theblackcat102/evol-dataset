import os
from setuptools import setup

with open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md")
) as infile:
    long_description = infile.read()

setup(
    name="evolinstruct",
    version="1.0.0",
    description="Evol existing instruction dataset to answer more diverse and complex answers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/theblackcat102/evol-dataset",
    author="Zhi-Rui Tam",
    license="Apache 2.0",
    packages=[
        "evolinstruct",
        "evolinstruct.instructions",
        "evolinstruct.autocompletes",
    ],
    package_data={"evolinstruct": ["**/*.txt"]},
    include_package_data=True,
    install_requires=[
        "Jinja2==3.1.2",
        "openai==0.27.8",
        "tqdm==4.65.0",
    ],
    extras_require={
        "dev": [
            "black",
            "flake8",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.10",
    ],
)
