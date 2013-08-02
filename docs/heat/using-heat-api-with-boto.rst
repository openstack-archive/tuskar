============================
Using the Heat API with Boto
============================


What is Boto?
-------------

Boto is a Python package that provides interfaces to Amazon Web
Services. It supports all the services (including the CloudFormations
API) that are needed by the Heat API.

https://github.com/boto/boto

http://docs.pythonboto.org/en/latest/ref/cloudformation.html

Prerequires
-----------

The latest version of 'boto' will not work(!) because they now use
a newer AWS signature (v2) that is not (yet) supported by Heat. The
2.4.x version of 'boto' will not work as well, because it lacks support
for setting the 'host' for the CloudFormations server. However, you can use
``pip`` to install the right version (and we can add the version to the tox
environment):

``$ pip install "boto==2.5.2"``

Configuration
-------------

Boto use the ``~/.boto`` config file to store settings. I'm pretty much
sure we can override this location and store the file in
``tuskar/etc/boto.conf``. But for testing, just use ``~/.boto``:

::

    [Boto]
    cfn_region_name = heat
    cfn_region_endpoint = HEAT_SERVER_HOSTNAME
    debug = True
    is_secure = False

    [Credentials]
    aws_access_key_id = EC2_KEY
    aws_secret_access_key = EC2_SECRET

The 'HEAT\_SERVER\_HOSTNAME' is the domain name or IP address of the
Heat API server (without 'http' !). The credentials must be generated on
the Heat server:

::

    $ source /root/keystonerc_admin
    $ keystone ec2-credentials-create

    +-----------+----------------------------------+
    |  Property |              Value               |
    +-----------+----------------------------------+
    |   access  | EC_KEY                           |
    |   secret  | EC2_SECRET                       |
    | tenant_id | 3661d05ad41e493fbcdec6826b9a7ba3 |
    |  user_id  | 4b7f47864e4948aaa16fdbcf774f8358 |
    +-----------+----------------------------------+

Note the ``ec2-credentials-create`` command will use the current
keystone user\_id (OS\_USERNAME=admin in keystonerc\_admin), if you want
to create credentials for other user, you need to change the
``keystonerc_admin`` file.

Usage
-----

Listing Stacks
~~~~~~~~~~~~~~

::

    from boto.cloudformation import CloudFormationConnection
    # FIXME: The 'port' and 'path' should be stored in config file...
    conn = CloudFormationConnection(port=8000, path='/v1')

    print conn.list_stacks()
