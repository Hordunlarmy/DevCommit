import os
import subprocess

from setuptools import find_packages, setup
from setuptools.command.install import install

with open("README.md", "r") as fh:
    long_description = fh.read()


class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        script_path = os.path.join(
            os.path.dirname(__file__), "scripts", "create_dcommit.py"
        )
        subprocess.call(["python3", script_path])


setup(
    name="DevCommit",
    version="0.1.4.3",
    author="HordunTech",
    author_email="horduntech@gmail.com",
    description=""" A command-line AI tool for autocommits """,
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://github.com/hordunlarmy/DevCommit",
    packages=find_packages(),
    install_requires=[
        "inquirerpy",
        "google-generativeai",
        "rich",
        "python-decouple",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "devcommit=devcommit.main:main",
            "create-dcommit=scripts.create_dcommit:create_dcommit",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.dcommit"],
    },
    data_files=[
        ("scripts", ["scripts/create_dcommit.py"]),
    ],
    cmdclass={
        "install": CustomInstallCommand,
    },
)
