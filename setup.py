
from distutils.core import setup


setup(
    name = "pysos",
    version = "1.1",
    author = "Jake Hunsaker",
    author_email = "jhunsaker@redhat.com",
    description = ("Utility to parse sosreports and make them pretty"),
    keywords = "pysos sosreport",
    scripts=['pysos/pysos'],
    packages=['pysos', 'pysos/kernel','pysos/opsys', 'pysos/network', 'pysos/rhev', 'pysos/config',\
    'pysos/rhevlcbridge', 'pysos/storage'],
)
