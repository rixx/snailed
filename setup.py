from setuptools import setup

setup(
    name="snailed",
    author="Tobias Kunze",
    author_email="r@rixx.de",
    url="https://github.com/rixx/snailed",
    packages=["src"],
    install_requires=[
        "defusedxml==0.7.1",
    ],
)
