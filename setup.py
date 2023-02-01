import re

from setuptools import setup

# inspired by https://github.com/Rapptz/discord.py/blob/master/setup.py

requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

version = ''
with open('valorantx/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

readme = ''
with open('README.md') as f:
    readme = f.read()

extras_require = {
    'local': ['urllib3>=1.26.12,<1.27'],
}

packages = ['valorantx', 'valorantx.models', 'valorantx.types', 'valorantx.ext.scrapers']

setup(
    name='valorantx',
    author='xStacia',
    url='https://github.com/staciax/valorantx',
    project_urls={
        "Issue tracker": "https://github.com/staciax/valorantx/issues",
    },
    version=version,
    packages=packages,
    license='MIT',
    description='An Asynchronous Unofficial Valorant API Wrapper for Python',
    long_description=readme,
    include_package_data=True,
    install_requires=requirements,
    extras_require=extras_require,
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
    ],
)
