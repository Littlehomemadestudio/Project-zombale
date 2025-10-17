from setuptools import setup, find_packages

setup(
    name="bale",
    version="2.5.0",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
    ],
    python_requires=">=3.8",
)

