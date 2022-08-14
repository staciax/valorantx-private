from setuptools import setup
import re

# inspired by https://github.com/Rapptz/discord.py/blob/master/setup.py

requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

version = ''
with open('valorant/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

readme = ''
with open('README.md') as f:
    readme = f.read()

packages = [
    'valorant',
    'valorant.models',
    'valorant.types',
]

setup(
    name='pylorant',
    author='xStacia',
    url='https://github.com/staciax/pylorant',
    project_urls={
        "Issue tracker": "https://github.com/staciax/pylorant/issues",
    },
    version=version,
    packages=packages,
    license='MIT',
    description='An Asynchronous Valorant API Wrapper for Python',
    long_description=readme,
    install_requires=requirements,
    python_requires='>=3.8.0',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
