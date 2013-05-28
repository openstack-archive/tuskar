Tuskar
======

Tuskar is playground for some ideas for an OpenStack management API.

Send pull requests!

-----------
Development
-----------

Tuskar source code should be pulled directly from git::

  git clone https://github.com/openstack/tuskar

Setting up a local environment for development can be done with tox::

    cd <your_src_dir>/tuskar

    # install prerequisites
    * Ubuntu/Debian:
    sudo apt-get install python-dev swig libssl-dev python-pip libmysqlclient-dev libxml2-dev libxslt-dev
    * Fedora/RHEL:
    sudo yum install python-devel swig openssl-devel python-pip mysql-libs libxml2-devel libxslt-devel

    sudo easy_install nose
    sudo pip install virtualenv setuptools-git flake8 tox

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
