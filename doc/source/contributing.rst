======================
Contributing to Tuskar
======================

Tuskar follows the OpenStack development processes for code and
communication. The `repository is hosted on git.openstack.org
<http://git.openstack.org/cgit/openstack/tuskar>`_, `bugs and
blueprints are on Launchpad <https://launchpad.net/tuskar>`_ and
we use the openstack-dev mailing list (subject `[tuskar]`) and
the `#tripleo` IRC channel for communication.

As Tuskar is under the TripleO umbrella of projects you will also
want to look at the `TripleO contributing guidelines
<http://docs.openstack.org/developer/tripleo-
incubator/CONTRIBUTING.html>`_.


Coding Standards
----------------

We comply with the `OpenStack coding standards
<http://docs.openstack.org/developer/hacking/>`_.

Be sure to familiarise yourself with `OpenStack's Gerrit Workflow
<http://docs.openstack.org/infra/manual/developers.html#development-workflow>`_.

Before submitting your code, please make sure you have completed
the following checklist:

#. Update the API docs (if needed)
#. Update the tests (if needed)


Finding your way around
~~~~~~~~~~~~~~~~~~~~~~~

There are various pieces of the codebase that may not be
immediately obvious to a newcomer to the project, so we attempt
to explain some of that in this section.

Where do the tuskar commands come from? (tuskar-api, tuskar-dbsync, etc)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The project-specific commands live in tuskar/cmd, and are
implementations that use the oslo.config project as a base. They
are generated and put into your venv when you run 'python
setup.py develop'.  Adding a new one consists of:

#. Creating a new file in tuskar/cmd
#. Adding the appropriate name and package reference to the
   entry\_points section of setup.cfg

How do I add a new controller?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Controllers are contained in tuskar/api/controllers/v2.py. To add
a new controller, you need to add an 'HTTP Representation' of
whatever model you wish to expose with this controller. This is a
simple python object that extends Base, and describes the key and
value types that the object will return. For example, say there
is a Foo model object you wish to return.

.. code-block:: python

    class Foo(Base):
        id = int
        name = wtypes.text
        fred = Fred  # Fred is another object defined in this file

Then add a controller for it (anywhere above the Controller class,
which is the last in the file. For example:

.. code-block:: python

    class FoosController(rest.RestController):
        @wsme_pecan.wsexpose([Foo])
        def get_all(self)
            result = []
            """Do some things to get your list of Foos"""
            return result

Lastly, add a reference to the controller in the Controller class at
the bottom of the file as so.

.. code-block:: python

    class Controller(object):
        foos = FoosController()

The name you give the controller above will be how it is accessed by
the client, so in the above case, you could get the list of foos
with.

.. code-block:: bash

    curl http://0.0.0.0:8585/v1/foos

For doing something simple, like a poc controller that doesn't
return any objects, you can return plain text as so

.. code-block:: python

    class FarkleController(rest.RestController):
        @wsme_pecan.wsexpose(None, wtypes.text)
        def get_all(self):
            return "Hi, I am farkle!"

Where are my changes to the app?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You may make a change to, say, a controller, and wonder why your
change does not seem to happen when you call your curl command on
that resource. This is because, at least at the current time, you
must ctrl+c to kill the tuskar-api server, and then restart it
again to pick up your changes.

How do I create a new model?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Models live in tuskar/db/sqlalchemy/. There are two files here of
relevance for describing the model (we will get to defining the
table in the next section), api.py and models.py. The models.py
file contains the definition of the columns to expose to the
client for the model objects, as well as a mapping of the object
in this file to the tablename define in the migration (below). In
api.py, we have utility methods, as well as validation rules and
other custom methods for interacting with the models.

How do I define the table for my new model?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is described in a migration file, located in
tuskar/db/sqlalchemy/migrate\_repo/versions/. Each new table or
change to an existing table should get a new file here with a
descriptive name, starting with a 3 digit number. Each new file
should increment the number to avoid collisions. The primary part of
this file is the definition of your table, which s done via a Table
object, and you describe the columns, using, surprisingly enough, a
Column object. There are upgrade nd downgrade methods in these
migrations to describe what to do for creating a given set of
tables, as well as dropping them, or rolling back to what was done
before the upgrade.

Writing and Running tests
~~~~~~~~~~~~~~~~~~~~~~~~~

We use testtools for our unit tests, and mox for mock objects.

You can run tests using Tox:

  .. code-block:: bash

    $ tox

This will run tests under Python 2.7 and verify `PEP 8
<http://www.python.org/dev/peps/pep-0008/>`_ compliance. The identical test
suite is run by OpenStack's Jenkins whenever you send a patch.
