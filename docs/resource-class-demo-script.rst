==========================
Resource Class Demo Script
==========================

Get a Resource Class
--------------------

::

    curl -H 'Accept: application/json' http://0.0.0.0:6385/v1/resource_classes/1

    {
      "service_type": "compute",
      "racks": [],
      "id": 1,
      "links": [{
        "href": "http://0.0.0.0:6385/v1/resource_classes/1",
        "rel": "self"
       }],
       "name": "test-chassis"
    }

Get the Resource Class Collection
---------------------------------

::

    curl -H 'Accept: application/json' http://0.0.0.0:6385/v1/resource_classes/

Create a Resource Class with a Rack
-----------------------------------

::

    curl -iX POST -H 'Content-Type: application/json' -H 'Accept: application/json' -d '
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
    ' http://0.0.0.0:6385/v1/resource_classes``

Update the Racks on a Resource Class (Remove Racks)
---------------------------------------------------

::

    curl -iX PUT -H 'Content-Type: application/json' -H 'Accept: application/json' -d '
       {
         "service_type": "compute",
         "name": "test-chassis",
         "racks":[]
       }
    ' http://0.0.0.0:6385/v1/resource_classes/13``

Update the Racks on a Resource Class (Add a Rack)
-------------------------------------------------

::

    curl -iX PUT -H 'Content-Type: application/json' -H 'Accept: application/json' -d '
       {
         "service_type": "compute",
         "name": "test-chassis",
         "racks":[
           {
             "id": 2,
             "links": [
               {
                  "href":"http://0.0.0.0:6385/v1/racks/2",
                  "rel":"self"
               }
             ]
           }
        ]
      }
    ' http://0.0.0.0:6385/v1/resource_classes/13``

Delete a Resource Class
-----------------------

::

    curl -iX DELETE -H 'Accept: application/json'  http://0.0.0.0:6385/v1/resource_classes/13
