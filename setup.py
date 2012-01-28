#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import codecs
import platform

try:
    from setuptools import setup, find_packages, Command
    from setuptools.command.test import test as TestCommand
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages, Command
    from setuptools.command.test import test as TestCommand

# Extract distribution meta values, hint taken from Celery <http://celeryproject.org>

import re
re_meta = re.compile(r'__(\w+?)__\s*=\s*(.*)')
re_vers = re.compile(r'VERSION\s*=\s*\((.*?)\)')
re_doc = re.compile(r'^"""(.+?)"""')
rq = lambda s: s.strip("\"'")

def add_default(m):
    attr_name, attr_value = m.groups()
    return ((attr_name, rq(attr_value)), )


def add_version(m):
    v = list(map(rq, m.groups()[0].split(", ")))
    return (("VERSION", ".".join(v[0:3]) + "".join(v[3:])), )


def add_doc(m):
    return (("doc", m.groups()[0]), )

pats = {re_meta: add_default,
        re_vers: add_version,
        re_doc: add_doc}
here = os.path.abspath(os.path.dirname(__file__))
meta_fh = open(os.path.join(here, "pyes/__init__.py"))
try:
    meta = {}
    for line in meta_fh:
        for pattern, handler in pats.items():
            m = pattern.match(line.strip())
            if m:
                meta.update(handler(m))
finally:
    meta_fh.close()


class QuickRunTests(TestCommand):
    extra_env = dict(SKIP_RLIMITS=1, QUICKTEST=1)

    def run(self, *args, **kwargs):
        for env_name, env_value in self.extra_env.items():
            os.environ[env_name] = str(env_value)
        TestCommand.run(self, *args, **kwargs)


install_requires = ["requests"]

#if not sys.platform.startswith("java"):
#    install_requires += [ "thrift", ]    
try:
    import importlib
except ImportError:
    install_requires.append("importlib")

try:
    # For Python >= 2.6
    import json
except ImportError:
    # For Python < 2.6 or people using a newer version of simplejson
    install_requires.append("simplejson")

py_version = sys.version_info
if not sys.platform.startswith("java") and sys.version_info < (2, 6):
    install_requires.append("multiprocessing==2.6.2.1")

if os.path.exists("README.rst"):
    long_description = codecs.open("README.rst", "r", "utf-8").read()
else:
    long_description = "See http://pypi.python.org/pypi/pyes"

setup(
    name='pyes',
    version=meta['VERSION'],
    description="Python Elastic Search driver",
    author=meta['author'],
    author_email=meta['contact'],
    url=meta['homepage'],
    platforms=["any"],
    license="BSD",
    packages=find_packages(exclude=['ez_setup', 'tests', 'tests.*', "docs.*"]),
    scripts=[],
    zip_safe=False,
    install_requires=install_requires,
    tests_require=['nose', 'nose-cover3', 'unittest2', 'simplejson'],
    cmdclass={"quicktest": QuickRunTests},
    test_suite="nose.collector",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search'
    ],
    entry_points={
        'console_scripts': [],
    },
    long_description=long_description,
)
