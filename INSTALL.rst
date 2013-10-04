==================
Installation Guide
==================

Tuskar source code should be pulled directly from git::

    git clone https://github.com/openstack/tuskar.git


Dependencies
------------

Setting up a local environment for development can be done with tox::

    # install prerequisites
    * Ubuntu/Debian:
    $ sudo apt-get install python-dev swig libssl-dev python-pip libmysqlclient-dev libxml2-dev libxslt-dev
    * Fedora/RHEL:
    $ sudo yum install python-devel swig openssl-devel python-pip mysql-devel libxml2-devel libxslt-devel
    # Note that as of Fedora 19, you need to use the community
      upstream for mysql, called mariadb-devel

    $ sudo pip install virtualenv setuptools-git flake8 tox

    $ cd <your_src_dir>/tuskar
    # create virtualenv
    $ tox -e py27

Note: if ``pip install`` fails due to an outdated setuptools, you can try to update it first::

    $ sudo pip install --upgrade setuptools


Configuration
-------------

Copy the sample configuration file:

::

    $ cp etc/tuskar/tuskar.conf.sample etc/tuskar/tuskar.conf

Edit the config file and uncomment the `heat_keystone` section at the bottom:

::

    [heat_keystone]

    username = heat
    password = heat
    tenant_name = admin
    auth_url = http://localhost:35357/v2.0
    insecure = True

Note: replace these values with credentials for our undercloud OpenStack. If
you're using `Devstack <http://devstack.org/>`_, the username and password are
printed out when `stack.sh` finishes its job.

You will need a local checkout of the tripleo-heat-templates. A
configuration entry is defined for this purpose: tht_local_dir should point
to your local copy of the tripleo-heat-templates.

    tht_local_dir = "/etc/tuskar/tripleo-heat-templates/"

At tuskar startup, if the directory specified by tht_local_dir in your
tuskar.conf doesn't exist startup will fail. You can clone the templates:

    (sudo) git clone https://github.com/openstack/tripleo-heat-templates.git /etc/tuskar/tripleo-heat-templates/

We need to initialise the database schema::

    # activate the virtualenv
    $ source .tox/py27/bin/activate

    # if you delete tuskar.sqlite this will force creation of tables again - e.g.
    # if you added a new resource table definitions etc in an existing migration
    # file
    $ tuskar-dbsync --config-file etc/tuskar/tuskar.conf

You can verify this was successful (in addition to seeing no error
output) with::

    $ sqlite3 tuskar.sqlite .schema

Then, launch the app and try curl to see if it works::

    $ tuskar-api --config-file etc/tuskar/tuskar.conf
    $ curl -v -X GET -H 'Accept: application/json' http://0.0.0.0:8585/v1/resource_classes/ | python -mjson.tool

Assuming this is your first time running with a new database, you should
simply get '[]' back from curl above. Currently the api supports only
json return type, so we request that in the example call.

Next, you can run a script to populate the DB with some sample data::

    $ python tools/sample_data.py

This will create 2 Resource Classes and three Racks. You need to have the Tuskar
API server running. You can see more examples of using the API at our `cURL
Commands page <https://github.com/openstack/tuskar/blob/master/docs/api/curl.rst>`_.


Running Tuskar API
------------------

Whenever you want to run the API again, just switch to the virtualenv and run
`tuskar-api` command:

::

    $ source .tox/py27/bin/activate
    $ tuskar-api --config-file etc/tuskar/tuskar.conf


Contributing
------------

For additional developer information, take a look at
`CONTRIBUTING.rst <https://github.com/openstack/tuskar/blob/master/CONTRIBUTING.rst>`_
and the
`Tuskar website <https://github.com/openstack/tuskar/blob/master/docs/index.rst>`_.
