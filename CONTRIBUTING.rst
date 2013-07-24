======================
Contributing to tuskar
======================

Pretty soon, tuskar will move to stackforge, using gerrit for reviews and
launchpad for bugs and blueprints. We're just getting started at this point
so, in the interim, we accept pull requests via github.

Coding Standards
----------------

We attempt to comply with the openstack coding standards, defined in
https://github.com/openstack-dev/hacking/blob/master/HACKING.rst

Before pushing your code, make sure it complies with the standards by
running:

  $ tox -e pep8

Also, before submitting your code, please make sure you have completed the
following checklist:

1. Update the tools/sample_data.py (if needed)
2. Update the API docs (if needed)
3. Update the tests (if needed)
4. Update `cURL commands <https://github.com/tuskar/tuskar/wiki/cURL-commands>`_
   page (if needed)

Getting Started
---------------


Set up tuskar development environment.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This assumes you have done all the basic setup as described in the README.  Run
the following::

  # creates symlinks for installed code.  Used for dev environment.
  $ python setup.py develop
  $ cp etc/tuskar/tuskar.conf.sample etc/tuskar/tuskar.conf

The config file changes are::

  $ openstack-config --set etc/tuskar/tuskar.conf database connection sqlite:///tuskar.sqlite
  $ openstack-config --set etc/tuskar/tuskar.conf DEFAULT debug true
  $ openstack-config --set etc/tuskar/tuskar.conf heat stack_name overcloud
  $ openstack-config --set etc/tuskar/tuskar.conf heat service_type orchestration
  $ openstack-config --set etc/tuskar/tuskar.conf heat_keystone username heat
  $ openstack-config --set etc/tuskar/tuskar.conf heat_keystone password heat
  $ openstack-config --set etc/tuskar/tuskar.conf heat_keystone tenant_name admin
  $ openstack-config --set etc/tuskar/tuskar.conf heat_keystone auth_url http://10.34.32.181:35357/v2.0
  $ openstack-config --set etc/tuskar/tuskar.conf heat_keystone insecure True

The command above is part of the openstack-utils package, so you will have to install 
that if you have not already.

Then::

  # if you delete tuskar.sqlite this will force creation of tables again - e.g.
  # if you added a new resource table definitions etc in an existing migration
  # file
  $ tuskar-dbsync --config-file etc/tuskar/tuskar.conf

You can verify this was successful (in addition to seeing no error output)
with::

  $ sqlite3 tuskar.sqlite .schema

Then, launch the app and try curl to see if it works::

  $ tuskar-api --config-file etc/tuskar/tuskar.conf
  $ curl -v -X GET -H 'Accept: application/json' http://0.0.0.0:6385/ | python -mjson.tool

Assuming this is your first time running with a new database, you should simply
get '[]' back from curl above. Currently the api supports only json return type,
so we request that in the example call.

Next, you can run a script to populate the DB with some sample data:

 $ python tools/sample_data.py

Finding your way around
~~~~~~~~~~~~~~~~~~~~~~~

There are various pieces of the codebase that may not be immediately obvious to
a newcomer to the project, so we attempt to explain some of that in this
section.

* Where do the tuskar commands come from? (tuskar-api, tuskar-dbsync, etc)

  The project-specific commands live in tuskar/cmd, and are implementations that
  use the oslo.config project as a base.  They are generated and put into your
  venv when you run 'python setup.py develop'. Adding a new one consists of:

  1. Creating a new file in tuskar/cmd
  2. Adding the appropriate name and package reference to the entry_points
     section of setup.cfg

* How do I add a new controller?

  Controllers are contained in tuskar/api/controllers/v1.py.  To add a new
  controller, you need to add an 'HTTP Representation' of whatever model you
  wish to expose with this controller.  This is a simple python object that
  extends Base, and describes the key and value types that the object will
  return.  For example, say there is a Foo model object you wish to return::

    class Foo(Base):
        id = int
        name = wtypes.text
        fred = Fred       # Fred is another object defined in this file

  Then add a controller for it (anywhere above the Controller class, which is
  the last in the file.  For example::

    class FoosController(rest.RestController):
        @wsme_pecan.wsexpose([Foo])
        def get_all(self)
            result = []
            """Do some things to get your list of Foos"""
            return result

  Lastly, add a reference to the controller in the Controller class at the
  bottom of the file as so::

    class Controller(object):
        foos = FoosController()

  The name you give the controller above will be how it is accessed by the
  client, so in the above case, you could get the list of foos with::

    curl http://0.0.0.0:6385/v1/foos

  For doing something simple, like a poc controller that doesn't return any
  objects, you can return plain text as so::

    class FarkleController(rest.RestController):
        @wsme_pecan.wsexpose(None, wtypes.text)
        def get_all(self):
            return "Hi, I am farkle!"

* Where are my changes to the app?

  There are two possible answers:

  1. You may make a change to, say, a controller, and wonder why your change 
     does not seem to happen when you call your curl command on that resource.
     This is because, at least at the current time, you must <ctrl>-c to kill
     the tuskar-api server, and then start it again to pick up your changes.
  2. You may have changed something that requires you to rerun 'python setup.py
     develop', such as changing or adding a new command in the cmd dir described
     above

* How do I create a new model?

  Models live in tuskar/db/sqlalchemy/.  There are two files here of relevance for
  describing the model (we will get to defining the table in the next section),
  api.py and models.py. The models.py file contains the definition of the
  columns to expose to the client for the model objects, as well as a mapping of
  the object in this file to the tablename define in the migration (below).
  In api.py, we have utility methods, as well as validation rules and other custom
  methods for interacting with the models.

* How do I define the table for my new model?

  This is described in a migration file, located in
  tuskar/db/sqlalchemy/migrate_repo/versions/. Each new table or change to an
  existing table should get a new file here with a descriptive name, starting
  with a 3 digit number.  Each new file should increment the number to avoid
  collisions.  The primary part of this file is the definition of your table,
  which s done via a Table object, and you describe the columns, using,
  surprisingly enough, a Column object. There are upgrade nd downgrade methods
  in these migrations to describe what to do for creating a given set of tables,
  as well as dropping them, or rolling back to what was done before the upgrade.

Writing Tests
~~~~~~~~~~~~~

So you want to write tests?  Great, here is how:

We use testtools for our unit tests, and mox for mock objects.

More details TBD
