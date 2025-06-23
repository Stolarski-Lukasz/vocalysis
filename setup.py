from setuptools import setup, find_packages


with open('README.md', 'r') as f:
    description = f.read()

setup(
    name='vocalysis',
    version='0.1.2',
    author='Łukasz Stolarski', 
    packages=find_packages(),
    install_requires=[
        'praat-parselmouth>=0.4.4',
        'numpy>=1.26.0',
    ],
    long_description=description,
    long_description_content_type='text/markdown',
    url="https://github.com/Stolarski-Lukasz/vocalysis.git",
    author="Łukasz Stolarski",
    description="A Python package for voice analysis using Praat and Parselmouth.",
    license="GNU General Public License v3.0 (GPLv3+)"
)
