.. _pyes-installation:

Installation
============

You can install PyES either via the Python Package Index (PyPI)
or from source.

To install using `pip`,

.. code-block:: sh

    $ pip install pyes

To install using `easy_install`,

.. code-block:: sh

    $ easy_install pyes

.. _pyes-installing-from-source:

Downloading and installing from source
--------------------------------------

Download the latest version of PyES from
http://pypi.python.org/pypi/pyes/

You can install it by doing the following,

.. code-block:: sh

    $ tar xvfz pyes-0.0.0.tar.gz
    $ cd pyes-0.0.0
    $ python setup.py build
    # python setup.py install # as root

.. _pyes-installing-from-git:

Using the development version
-----------------------------

You can clone the repository by doing the following

.. code-block:: sh

    $ git clone git://github.com/aparo/pyes.git
    $ cd pyes
    $ python setup.py develop

To update:

.. code-block:: sh

    $ cd pyes
    $ git pull origin master
