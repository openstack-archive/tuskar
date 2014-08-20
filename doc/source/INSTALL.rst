==================
Installation Guide
==================

The Tuskar source code should be pulled directly from git::

    git clone https://git.openstack.org/openstack/tuskar


Dependencies
------------

Setting up a local environment for development can be done with tox::

    # install prerequisites
    * Ubuntu/Debian:
    $ sudo apt-get install python-dev swig libssl-dev python-pip libmysqlclient-dev libxml2-dev libxslt-dev gcc
    * Fedora/RHEL:
    $ sudo yum install python-devel swig openssl-devel python-pip mysql-devel libxml2-devel libxslt-devel gcc
    # Note that as of Fedora 19, you need to use the community
      upstream for mysql, called mariadb-devel

    $ sudo pip install virtualenv setuptools-git flake8 tox

.. note::
    An `issue with tox <https://bugs.launchpad.net/openstack-ci/+bug/1274135>`
    requires that you use a version <1.70 or >= 1.7.2.

Now create your virtualenv::

    $ cd <your_src_dir>/tuskar
    $ tox -e py27

.. note::

    If ``pip install`` fails due to an outdated setuptools, you can try to
    update it first::

        $ sudo pip install --upgrade setuptools


Configuration
-------------

Copy the sample configuration file:

::

    $ cp etc/tuskar/tuskar.conf.sample etc/tuskar/tuskar.conf

We need to tell tuskar where to connect to database. Edit the config file in
``database`` section and change

::

    #connection=<None>

to

::

    connection=sqlite:///tuskar/tuskar.sqlite

We need to initialise the database schema::

    # activate the virtualenv
    $ source .tox/py27/bin/activate

    # if you delete tuskar.sqlite this will force creation of tables again - e.g.
    # if you added a new resource table definitions etc in an existing migration
    # file
    $ tuskar-dbsync --config-file etc/tuskar/tuskar.conf

You can verify this was successful (in addition to seeing no error output)
with::

    $ sqlite3 tuskar/tuskar.sqlite .schema

Then, launch the app::

    $ tuskar-api --config-file etc/tuskar/tuskar.conf

You can then verify that everything worked by running.::

    $ curl -v -X GET -H 'Accept: application/json' http://0.0.0.0:8585/v2/plans/ | python -mjson.tool

This command should return JSON with an empty result set.

Keystone Configuration
^^^^^^^^^^^^^^^^^^^^^^

By default, Tuskar is configured to skip authentication for REST API calls.
Keystone authentication can be enabled by making the appropriate changes to the
``tuskar.conf`` file as described in the `keystone documentation
<http://docs.openstack.org/developer/keystone/configuringservices.html>`

Running Tuskar API
------------------

Whenever you want to run the API again, just switch to the virtualenv and run
`tuskar-api` command:

::

    $ source .tox/py27/bin/activate
    $ tuskar-api --config-file etc/tuskar/tuskar.conf


Contributing
------------

For additional developer information, take a look at `CONTRIBUTING.rst
<docs/CONTRIBUTING.rst>`_ and the `developer documentation <docs/index.rst>`_.
