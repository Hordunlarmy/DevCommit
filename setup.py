from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess


class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        subprocess.call(['python3', '-m', 'scripts.create_dcommit'])


setup(
    name='DevCommit',
    version='0.1.0',
    author='HordunTech',
    author_email='horduntech@gmail.com',
    description='A command-line AI tool for autocommits',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/hordunlarmy/DevCommit',
    packages=find_packages(),
    install_requires=[
        'inquirerpy',
        'google-generativeai',
        'rich',
        'python-decouple',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'devcommit=main:main',
            'create-dcommit=scripts.create_dcommit:create_dcommit',
        ],
    },    include_package_data=True,
    package_data={
        '': ['*.dcommit'],
    },
    data_files=[
        ('scripts', ['scripts/create_dcommit.py']),
    ],
    cmdclass={
        'install': CustomInstallCommand,
    }
)
