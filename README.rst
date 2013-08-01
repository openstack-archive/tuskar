======
Tuskar
======
.. image:: https://travis-ci.org/tuskar/tuskar.png?branch=master
   :target: http://travis-ci.org/tuskar/tuskar

What is Tuskar?
---------------
Tuskar gives administrators the ability to control how and where
OpenStack services are deployed across the datacenter. Using Tuskar,
administrators divide hardware into "resource classes" that allow
predictable elastic scaling as cloud demands grow. This resource
orchestration allows Tuskar users to ensure SLAs, improve performance,
and maximize utilization across the datacenter.

Tuskar services are available via a RESTful API and management console
through which administrators are able to classify their hardware and
define their datacenters. In addition, Tuskar components provide
administrators with performance monitoring, health statistics, and
usage metrics, aiding in capacity planning and hardware procurement
decisions.

For additional information, take a look at the `Tuskar
documentation <https://github.com/tuskar/tuskar/blob/master/docs/index.rst>`_.

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
