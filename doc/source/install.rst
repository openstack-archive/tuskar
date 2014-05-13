============================
Developer Installation Guide
============================

The Tuskar source code should be pulled directly from git.

.. code-block:: bash

    git clone https://git.openstack.org/openstack/tuskar


Dependencies
------------

Setting up a local environment for development can be done with
tox.

.. code-block:: bash

    # install prerequisites
    * Fedora/RHEL:
    $ sudo yum install python-devel python-pip libxml2-devel \
        libxslt-devel postgresql-devel mariadb-devel

    * Ubuntu/Debian:
    $ sudo apt-get install python-dev python-pip libxml2-dev \
        libxslt-dev libpq-dev libmysqlclient-dev

.. note::

    If you wish you run Tuskar against MySQL or PostgreSQL you
    will need also install and configure these at this point.
    Otherwise you can run Tuskar with an sqlite database.

To run the Tuskar test suite you will also need to install Tox.

.. code-block:: bash

    $ sudo pip install tox

.. note::
    An `issue with tox <https://bugs.launchpad.net/openstack-ci/+bug/1274135>`_
    requires that you use a version <1.70 or >= 1.7.2.

Now create your virtualenv.

.. code-block:: bash

    $ cd <your_src_dir>/tuskar
    $ tox -e venv


.. note::

    If ``pip install`` fails due to an outdated setuptools, you
    can try to update it first.

    .. code-block:: bash

        $ sudo pip install --upgrade setuptools

To run the test suite use the following command. This will run
against Python 2.6, Python 2.7 and run the `flake8
<https://flake8.readthedocs.org>`_ code linting.

.. code-block:: bash

    $ tox

.. note::

    If you only have access to Python 2.6 or 2.7 locally pass
    in `-e py26` or `-e py27` respectively.


Configuration
-------------

Copy the sample configuration file:

.. code-block:: bash

    $ cp etc/tuskar/tuskar.conf.sample etc/tuskar/tuskar.conf

We need to tell tuskar where to connect to database. Edit the
config file in ``database`` section and change

.. code-block:: ini

    #connection=<None>

to

.. code-block:: ini

    connection=sqlite:///tuskar/tuskar.sqlite

.. note::

    If you are using a different database backend, you will need
    to enter a `SQLAlchemy compatible conection string
    <http://docs.sqlalchemy.org/en/latest/core/engines.html
    #database-urls>`_ for this setting.

We need to initialise the database schema.

.. code-block:: bash

    # activate the virtualenv
    $ source .tox/venv/bin/activate

    # if you delete tuskar.sqlite this will force creation of tables again - e.g.
    # if you added a new resource table definitions etc in an existing migration
    # file
    $ tuskar-dbsync --config-file etc/tuskar/tuskar.conf

You can verify this was successful (in addition to seeing no
error output) with.

.. code-block:: bash

    $ sqlite3 tuskar/tuskar.sqlite .schema

Then, launch the app.

.. code-block:: bash

    $ tuskar-api --config-file etc/tuskar/tuskar.conf

You can then verify that everything worked by running.

.. code-block:: bash

    $ curl -v -X GET -H 'Accept: application/json' http://0.0.0.0:8585/v2/plans/ | python -mjson.tool

This command should return JSON with an empty result set.


Running Tuskar API
------------------

Whenever you want to run the API again, just switch to the
virtualenv and run `tuskar-api` command.

.. code-block:: bash

    $ source .tox/venv/bin/activate
    $ tuskar-api --config-file etc/tuskar/tuskar.conf


Loading Initial Roles
---------------------

Tuskar needs to be provided with a set of roles that can be added
to a deployment plan. The following steps will add the roles from
the TripleO Heat Templates repository.

.. code-block:: bash

    $ git clone http://git.openstack.org/cgit/openstack/tripleo-heat-templates/
    $ cd tripleo-heat-templates
    $ tuskar-load-roles --config-file etc/tuskar/tuskar.conf \
        -r compute.yaml \
        -r controller.yaml

After this, if the Tuskar API isn't running, start it with the
above command and the following curl command should show you the
loaded roles.

.. code-block:: bash

    $ curl -v -X GET -H 'Accept: application/json' http://0.0.0.0:8585/v2/roles/ | python -mjson.tool



Keystone Configuration
----------------------

By default, Tuskar is configured to authenticate with Keystone
for REST API calls. For development, Keystone authentication can
be disabled by updating the ``tuskar.conf`` and changing the
``auth_strategy`` to equal ``noauth ``.


Contributing
------------

For additional developer information, take a look at
:doc:`the contributing guide <contributing>`.
