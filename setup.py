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
)
