import os
from setuptools import setup

def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pysos",
    version = "1.1",
    author = "Jake Hunsaker",
    author_email = "jhunsaker@redhat.com",
    description = ("Utility to parse sosreports and make them pretty"),
    license = "GPL",
    keywords = "pysos sosreport",
    packages=['pysos'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: GPL License",
    ],
)
