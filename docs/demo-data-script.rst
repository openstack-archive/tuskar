================
Demo Data Script
================

This document details the beginning of the walkthrough script for the
 Tuskar demo

To use this, clear your database and run the commands below.  The result
should be a HEAT template with 6 compute Nodes and 1 non-compute Node.

N.B. The HEAT template does not define availability zones for the nodes.
Therefore the nodes could be deployed onto any rack.  This will be fixed
in a subsequent patch.

**Note:** The commands below are useful for experimenting with different
creation scenarios, but the exact data center described therein can also
be created by running:

::

    python tools/sample_data/py

from your development environment.

Create Racks
------------

This command creates three Racks.  Two Racks are assigned to the
compute Resource Class and contain three Baremetal Nodes each. One Rack
is designated to the non-compute Resource Class and contains 1 Baremetal
Node only.

::

    curl -vX POST -H 'Content-Type: application/json' -H 'Accept: application/json' -v -d  '
    {
      "subnet": "192.168.1.0/255",
      "name": "compute_1",
      "capacities": [{
        "name": "total_cpu",
        "value": "64"
      }, {
        "name": "total_memory",
        "value": "1024"
      }],
      "nodes": [
      {
        "id": "nova_bare_metal_1"
      },
      {
        "id": "nova_bare_metal_2"
      }, 
      {
        "id": "nova_bare_metal_3"
      }
      ],
      "slots": 3
    }
    ' http://0.0.0.0:6385/v1/racks

    curl -vX POST -H 'Content-Type: application/json' -H 'Accept: application/json' -v -d  '
    {
      "subnet": "192.168.2.0/255",
      "name": "compute_2",
      "capacities": [{
        "name": "total_cpu",
        "value": "64"
      }, {
        "name": "total_memory",
        "value": "1024"
      }],
      "nodes": [
      {
        "id": "nova_bare_metal_4"
      },
      {
        "id": "nova_bare_metal_5"
      }, 
      {
        "id": "nova_bare_metal_6"
      }
      ],
      "slots": 3
    }
    ' http://0.0.0.0:6385/v1/racks

    curl -vX POST -H 'Content-Type: application/json' -H 'Accept: application/json' -v -d  '
    {
      "subnet": "192.168.2.0/255",
      "name": "non_compute",
      "capacities": [{
        "name": "total_cpu",
        "value": "64"
      }, {
        "name": "total_memory",
        "value": "1024"
      }],
      "nodes": [
      {
        "id": "nova_bare_metal_7"
      }],
      "slots": 3
    }
    ' http://0.0.0.0:6385/v1/racks

Create Resource Classes
-----------------------

This command creates two Resource Classes.  The compute Resource Class contains two Racks
and a total of six Nodes.  The non-compute Resoure Class contains one Rack and one Node.

::

    curl -iX POST -H 'Content-Type: application/json' -H 'Accept: application/json' -d '
        {
              "name": "compute-rc", 
              "service_type":"compute",
              "racks": [
                  { 
                    "id":1,
                    "links":[{"href":"http://0.0.0.0:6385/v1/racks/1","rel":"self"}]
                  },
                  { 
                    "id":2,
                    "links":[{"href":"http://0.0.0.0:6385/v1/racks/2","rel":"self"}]
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

    curl -iX POST -H 'Content-Type: application/json' -H 'Accept: application/json' -d '
        {
              "name": "non-compute-rc", 
              "service_type":"not_compute",
              "racks": [
                  { 
                    "id":3,
                    "links":[{"href":"http://0.0.0.0:6385/v1/racks/3","rel":"self"}]
                  }
               ]
          }
    ' http://0.0.0.0:6385/v1/resource_classes

Generate HEAT Template
----------------------

This command generates the HEAT template based on the Tuskar description.

::

    curl http://0.0.0.0:6385/v1/data_centers
