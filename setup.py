"""ownAI is an open source platform to run your own AI applications."""
from pathlib import Path
from setuptools import find_packages, setup

setup(
    name='ownAI',
    version='0.0.0',
    description='Run your own AI',
    url='https://ownai.org',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
    ],
    long_description=(Path(__file__).parent / 'README.md').read_text(),
    long_description_content_type='text/markdown'
)
