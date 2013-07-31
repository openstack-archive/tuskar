Tuskar
======
.. image:: https://travis-ci.org/tuskar/tuskar.png?branch=master
   :target: http://travis-ci.org/tuskar/tuskar

What is Tuskar?
---------------

Tuskar is a playground for some ideas for an OpenStack management API.
For additional information, take a look at the `Tuskar
website <https://github.com/tuskar/tuskar/blob/master/docs/index.rst>`_.

Developer Information
---------------------

Tuskar source code should be pulled directly from git::

    git clone https://github.com/tuskar/tuskar.git

Setting up a local environment for development can be done with tox::

    cd <your_src_dir>/tuskar

    # install prerequisites
    * Ubuntu/Debian:
    sudo apt-get install python-dev swig libssl-dev python-pip libmysqlclient-dev libxml2-dev libxslt-dev
    * Fedora/RHEL:
    sudo yum install python-devel swig openssl-devel python-pip mysql-devel libxml2-devel libxslt-devel
    # Note that as of Fedora 19, you need to use the community
      upstream for mysql, called mariadb-devel

    sudo easy_install nose
    sudo pip install virtualenv setuptools-git flake8 tox
    # With the exception of flake8, all of the above are also
      available for fedora via yum

    # create virtualenv
    tox -evenv -- echo 'done'

    # activate the virtualenv
    source .tox/venv/bin/activate

    # run testr init
    testr init

    # run pep8/flake8 checks
    flake8

    # run unit tests
    testr run

    # deactivate the virtualenv
    deactivate

For additional developer information, take a look at the `Tuskar
website <https://github.com/tuskar/tuskar/blob/master/docs/index.md>`_.

Contributing
~~~~~~~~~~~~

Please see
`CONTRIBUTING.md <https://github.com/tuskar/tuskar/blob/master/CONTRIBUTING.md>`_
for details on how to contribute.

Send pull requests!
