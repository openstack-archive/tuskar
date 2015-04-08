============================
cURL Commands for API ver. 2
============================

.. _index:

Resources
---------
-  `Plan`_
-  `Role`_


Plan
----


Example of JSON Representation of Plan
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    {
      "created_at": "2014-09-26T20:23:14.222815",
      "description": "Development testing cloud",
      "name": "dev-cloud",
      "parameters":
      [
        {
          "constraints":
          [
            {
              "constraint_type": "range",
              "definition":
              {
                "min": "0"
              },
              "description": "Can't be less than zero"
            }
          ],
          "default": "0",
          "description": "The number of cinder storage nodes to deploy"
          "hidden": False,
          "label": "The number of cinder storage nodes to deploy",
          "name": "Cinder-Storage-1::count",
          "parameter_type": "number",
          "value": "0"
        },
        {
          "constraints": []
          "default": "guest",
          "description": "The password for RabbitMQ",
          "hidden": true,
          "label": null,
          "name": "compute-1::RabbitPassword",
          "parameter_type: "string"
          "value": "secret-password"
        }
      ],
      "roles":
      [
        {
          "description": "OpenStack hypervisor node. Can be wrapped in a ResourceGroup for scaling.\n",
          "name": "compute",
          "uuid": "b7b1583c-5c80-481f-a25b-708ed4a39734",
          "version": 1
        }
      ],
      "updated_at": null,
      "uuid": "53268a27-afc8-4b21-839f-90227dd7a001"
    }



List All Plans
~~~~~~~~~~

::

    curl -v -X GET -H 'Content-Type: application/json' -H 'Accept: application/json' http://0.0.0.0:8585/v2/plans/


Retrieve a Single Plan
~~~~~~~~~~~~~~~~~~~~~~

::

    curl -v -X GET -H 'Content-Type: application/json' -H 'Accept: application/json' http://0.0.0.0:8585/v2/plans/53268a27-afc8-4b21-839f-90227dd7a001


Create a New Plan
~~~~~~~~~~~~~~~~~

::

    curl -v -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -d  '
     {
       "name": "dev-cloud",
       "description": "Development testing cloud",
     }
     ' http://0.0.0.0:8585/v2/plans

This command will create new Plan without any Roles associated with it.
To assign a Role to Plan see `How to Add a Role to a Plan <#adding-a-role-to-a-plan>`_.


Delete an Existing Plan
~~~~~~~~~~~~~~~~~~~~~~~

::

    curl -v -X DELETE http://localhost:8585/v2/plans/53268a27-afc8-4b21-839f-90227dd7a001


Changing a Plan’s Configuration Values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    curl -v -X PATCH -H 'Content-Type: application/json' -H 'Accept: application/json' -d '
    [
      {
        "name" : "database_host",
        "value" : "10.11.12.13"
      },
      {
        "name" : "database_password",
        "value" : "secret"
      }
    ]
    ' http://0.0.0.0:8585/v2/plans/53268a27-afc8-4b21-839f-90227dd7a001

You can change only existing parameters in Plan.

Retrieve a Plan’s Template Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    curl -v -X GET -H 'Content-Type: application/json' -H 'Accept: application/json' http://0.0.0.0:8585/v2/plans/53268a27-afc8-4b21-839f-90227dd7a001/templates

Example of JSON representation:

::

    {
      "environment.yaml" : "... content of template file ...",
      "plan.yaml" : "... content of template file ...",
      "provider-compute-1.yaml" : "... content of template file ..."
    }

`back to top <#index>`_


Role
----


Example of JSON Representation of Role
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    {
      "description": "OpenStack hypervisor node. Can be wrapped in a ResourceGroup for scaling.\n",
      "name": "compute",
      "uuid": "b7b1583c-5c80-481f-a25b-708ed4a39734",
      "version": 1
    }

Retrieving Possible Roles
~~~~~~~~~~~~~~~~~~~~~~~~~

::

    curl -v -X GET -H 'Content-Type: application/json' -H 'Accept: application/json' http://0.0.0.0:8585/v2/roles/


Adding a Role to a Plan
~~~~~~~~~~~~~~~~~~~~~~~

::

    curl -v -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -d  '
     {
       "uuid": "b7b1583c-5c80-481f-a25b-708ed4a39734"
     }
     ' http://0.0.0.0:8585/v2/plans/53268a27-afc8-4b21-839f-90227dd7a001


Removing a Role from a Plan
~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    curl -v -X DELETE http://localhost:8585/v2/plans/53268a27-afc8-4b21-839f-90227dd7a001/roles/b7b1583c-5c80-481f-a25b-708ed4a39734

`back to top <#index>`_
