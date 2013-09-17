=============
cURL Commands
=============

Resources
---------

-  `Rack <#rack>`_
-  `Flavor <#flavor>`_
-  `ResourceClass <#resource_class>`_
-  `DataCenter <#data_center>`_
-  `Node <#node>`_

Rack
----

create
~~~~~~

::

    curl -vX POST -H 'Content-Type: application/json' -H 'Accept: application/json' -v -d  '
     {
       "subnet": "192.168.1.0/255",
       "name": "my_rack",
       "capacities": [{
         "name": "total_cpu",
         "value": "64",
         "unit": "count"
       }, {
         "name": "total_memory",
         "value": "1024",
         "unit": "MiB"
       }],
       "nodes": [{
         "id": "123"
       }, {
         "id": "345"
       }],
       "slots": 1
     }
     ' http://0.0.0.0:6385/v1/racks

create with ResourceClass
~~~~~~~~~~~~~~~~~~~~~~~~~

::

    curl -vX POST -H 'Content-Type: application/json' -H 'Accept: application/json' -v -d  '
     {
       "subnet": "192.168.1.0/255",
       "name": "my_rack",
       "capacities": [{
         "name": "total_cpu",
         "value": "64",
         "unit": "cpu"
       }, {
         "name": "total_memory",
         "value": "1024",
         "unit": "MB"
       }],
       "nodes": [{
         "id": "123"
       }, {
         "id": "345"
       }],
       "slots": 1,
       "resource_class":{
            "id":1,
            "links":[
               {
                  "href":"http://0.0.0.0:6385/v1/resource_clases/1",
                  "rel":"self"
               }
            ]
         }
     }
     ' http://0.0.0.0:6385/v1/racks

delete
~~~~~~

::

    curl -vX DELETE http://localhost:6385/v1/racks/1

update
~~~~~~

::

    curl -v -X PUT -H 'Content-Type: application/json' -H 'Accept: application/json' -v -d '{ "name": "new_name" }' http://0.0.0.0:6385/v1/racks/1

update (change nodes to Rack 1)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    curl -v -X PUT -H 'Content-Type: application/json' -H 'Accept: application/json' -v -d '{ "nodes": [ { "id": "1" }, { "id": "2"}] }' http://0.0.0.0:6385/v1/racks/1

`back to top <#index>`_

Flavor
------

This resource only exists as part of a ResourceClass.

create a new Flavor for a specific ResourceClass
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    curl -v -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -v -d '
     {
                "max_vms": 10,
                "name": "tiny",
                "capacities":
                [
                    {
                        "value": "1",
                        "name": "cpu",
                        "unit": "count"
                    },
                    {
                        "value": "512",
                        "name": "memory",
                        "unit": "MiB"
                    },
                    {
                        "value": "512",
                        "name": "storage",
                        "unit": "GiB"
                    }
                ]
      }'
     http://0.0.0.0:6385/v1/resource_classes/1/flavors``

Flavors can also be created as part of `ResourceClass create <#rc_with_flavors>`_ operation:

get Flavor(s) for a particular ResourceClass
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    curl -H "Accept: application/xml" http://0.0.0.0:6385/v1/resource_classes/1/flavors(/2)

delete a specific Flavor from a given ResourceClass
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    curl -X DELETE -H "Accept: application/xml" http://0.0.0.0:6385/v1/resource_classes/1/flavors/1

update an existing Flavor in a specified ResourceClass
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    curl -v -X PUT -H 'Content-Type: application/json' -H 'Accept: application/json' -v -d '
         {
            "capacities":
            [
                {
                    "value": "5000",
                    "name": "cpu",
                    "unit": "count"
                },
                {
                    "value": "1111",
                    "name": "memory",
                    "unit": "MiB"
                },
                {
                    "value": "2222",
                    "name": "storage",
                    "unit": "GiB"
                }
            ],
            "max_vms": 9999,
            "name": "tiny_update"     }'
     http://0.0.0.0:6385/v1/resource_classes/1/flavors/3``

**NOTE:** The above operation can be performed to change only part of a
given flavor - such as updating the name or max\_vms, or even a specific
capacity. The body of the PUT request will determine what is updated.
For example, to update the 'cpu' capacity and 'max\_vms':

::

    curl -v -X PUT -H 'Content-Type: application/json' -H 'Accept: application/json' -v -d '
     {
       "max_vms": 1234,
        "capacities" :  [
                           {  "name": "cpu",
                              "value" : "1",
                             "unit" : "count"  }
                        ]
     }'
     http://0.0.0.0:6385/v1/resource_classes/1/flavors/3``

`back to top <#index>`_

ResourceClass
-------------

get a specific ResourceClass
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    curl -H 'Accept: application/json' http://0.0.0.0:6385/v1/resource_classes/1

response
^^^^^^^^

::

    {
        "id":11,
        "name":"test-chassis",
        "service_type":"compute",
        "racks":[
           {
              "id":1,
              "links":[
                 {
                    "href":"http://0.0.0.0:6385/v1/rack/1",
                    "rel":"self"
                 }
              ]
           }
        ],
        "links":[
           {
              "href":"http://0.0.0.0:6385/v1/resource_classes/11",
              "rel":"self"
           }
        ]
     }

get collection
~~~~~~~~~~~~~~

::

    curl -H 'Accept: application/json' http://0.0.0.0:6385/v1/resource_classes

create without Racks
~~~~~~~~~~~~~~~~~~~~

::

      curl -iX POST -H 'Content-Type: application/json' -H 'Accept: application/json' -d '
      {
        "service_type": "compute",
        "name": "test-chassis"
      }
    ' http://0.0.0.0:6385/v1/resource_classes

create with Rack and Flavor definitions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    curl -iX POST -H 'Content-Type: application/json' -H 'Accept: application/json' -d '
         {
                "name": "test-chassis",
                "service_type":"compute",
                "racks": [
                    { "id":1,
                      "links":[{"href":"http://0.0.0.0:6385/v1/racks/1","rel":"self"}]
                    }
                 ],
                 "flavors": [
                     { "name" : "x-large",
                       "capacities" : [
                          {   "name": "cpu",
                              "value" : "4",
                              "unit" : "count" },
                          {   "name": "memory",
                              "value" : "8192",
                              "unit" : "MiB" },
                          {   "name": "storage",
                              "value" : "1024",
                              "unit" : "GiB" }
                       ]
                     }
                ]
           }
     ' http://0.0.0.0:6385/v1/resource_classes

**as a one-liner (copy/paste)**

::

    curl -iX POST -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{"service_type": "compute_1","name": "test-chassis", "service_type":"compute","racks":[{"id":1,"links":[{"href":"http://0.0.0.0:6385/v1/racks/1","rel":"self"}]}], "flavors": [{"name" : "x-large", "capacities" : [ { "name": "cpu", "value" : "4", "unit" : "count" }, { "name": "memory", "value" : "8192", "unit" : "MiB" }, { "name": "storage", "value" : "1024", "unit" : "GiB" }]}]}' http://0.0.0.0:6385/v1/resource_classes

update
~~~~~~

To add or remove Racks on a ResourceClass, simply do an update and alter
the racks array attribute accordingly.

::

    curl -iX PUT -H 'Content-Type: application/json' -H 'Accept: application/json' -d '
       {
         "service_type": "compute",
         "name": "test-chassis",
         "racks":[
           {
             "id": 1,
             "links": [
               {
                  "href":"http://0.0.0.0:6385/v1/racks/1",
                  "rel":"self"
               }
             ]
           }
         ]
       }
     ' http://0.0.0.0:6385/v1/resource_classes/13``

delete
~~~~~~

::

    curl -X DELETE http://0.0.0.0:6385/v1/resource_classes/1

`back to top <#index>`_

DataCenter
----------

provision all
~~~~~~~~~~~~~

This will provision the data center according to its description in
Tuskar.

::

    curl -XPOST -H 'Content-Type:application/json' -H 'Accept: application/json' http://0.0.0.0:6385/v1/data_centers/

`back to top <#index>`_

Node
----

Get Collection
~~~~~~~~~~~~~~

::

    curl http://0.0.0.0:6385/v1/nodes/

response
^^^^^^^^

::

    [
     {
      "node_id": "0e3ab3d3-bd85-40bd-b6a1-fae484040825",
      "id": "1",
      "links": [
                {
                 "href": "http://127.0.0.1:6385/v1/node/1",
                 "rel": "self"
                }
               ],
      "rack": {
               "id": 1,
               "links":
                       [
                        {
                         "href": "http://127.0.0.1:6385/v1/racks/1",
                         "rel": "self"
                        }
                       ]
              }
     }
    ]

Retrieve a single Node
~~~~~~~~~~~~~~~~~~~~~~

::

    curl http://0.0.0.0:6385/v1/nodes/1

response
^^^^^^^^

::

    {
     "node_id": "0e3ab3d3-bd85-40bd-b6a1-fae484040825",
     "id": "1",
     "links":
             [
              {
               "href": "http://127.0.0.1:6385/v1/node/1",
               "rel": "self"
              }
             ],
     "rack":
            {
             "id": 1,
             "links":
                     [
                      {
                       "href": "http://127.0.0.1:6385/v1/racks/1",
                       "rel": "self"
                      }
                     ]
            }
    }

`back to top <#index>`_
