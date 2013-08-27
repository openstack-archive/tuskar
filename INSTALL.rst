==================
Installation Guide
==================

Tuskar source code should be pulled directly from git::

    git clone https://github.com/stackforge/tuskar.git

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

For additional developer information, take a look at
`CONTRIBUTING.rst <https://github.com/stackforge/tuskar/blob/master/CONTRIBUTING.rst>`_
and the
`Tuskar website <https://github.com/stackforge/tuskar/blob/master/docs/index.rst>`_.
