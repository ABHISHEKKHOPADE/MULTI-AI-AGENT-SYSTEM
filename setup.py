from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="MULTI-AI AGENT",
    version="0.1",
    author="a",
    packages=find_packages(),
    install_requires=requirements,
)
