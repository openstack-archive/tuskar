# Tuskar API Draft

## ERD diagram:

* 05-30-2013: [version 1.0](./img/model_v1.jpg)
* 06-03-2013: [version 2.0](./img/model_v2.jpg)
* 06-04-2013: [version 3.0](./img/model_v3.jpg)
* 16-07-2013: [version 4.0](./img/model_v4.jpg)

## Introduction and Concepts

The main resources in the Tuskar API are:
<a name="index"></a>

* [ResourceClass](#resource_class)
  A ResourceClass can be thought of as a cloud 'building block'. It has a
  'type' that describes its purpose ('compute' or 'storage' for example).
  A ResourceClass consists of a set of hardware racks and defines the types
  of VM instances that can be supported by the physical Nodes in those Racks

* [Rack](#rack)
  A Rack can be thought of as a server Rack in a datacenter. It is a grouping
  of physical compute nodes that are assigned to a given ResourceClass and
  can be managed as a single unit.

* [Flavor](#flavor)
  A Flavor is a hardware configuration and its definition is aligned with the
  "instance_type" (aka 'Flavor') used in the OpenStack
  [Nova API](http://docs.openstack.org/api/openstack-compute/2/content/concepts.html).
  Flavors are defined for a given ResourceClass and semantically describe
  the types of compute instances that can be launched for that
  ResourceClass. Each Flavor has a set of Capacities that describe a particular
  aspect of the hardware configuration, such as cpu, memory or storage.

* [Capacity](#capacity)
  This is an abstraction used by both the Flavor and the Rack models. A given
  Capacity describes a particular aspect of a hardware configuration - such as
  cpu, memory, or storage. A Flavor is defined by a set of Capacities whilst
  a Rack maintains the aggregate Capacities of the Nodes it contains.

* [Node](#node)
  A Node is a single physical compute unit. A Rack resource consists of a
  number of Nodes and each Node corresponds to a compute Node in Nova Bare
  Metal (or eventually, in Ironic).

## Types

| Name          | Explanation                                                       |
|:--------------|:------------------------------------------------------------------|
| `String`        | JSON string                                                     |
| `URL`           | Absolute URL                                                    |
| `Array[T]`      | Array where each entry has type T                               |
| `Ref[T]`        | A reference to a T, used to model relations, the T is a valid Resource indentifier  |
| `Struct`        | A structure with sub-attributes                                 |
| `Collection`    | Grouping of resources containing an Array of resources of type T, as well as attributes and actions for the grouping |

## Common attributes:

| Attribute     | Type                       | Description                                |
|---------------|----------------------------|--------------------------------------------|
| id            | Ref(self)                  | Resource identifier                        |
| name          | String                     | Human readable name                        |

<hr/>

## ResourceClass
<a name="resource_class"></a>

The ResourceClass describes the list of instance types (flavors) and the
array of references to the Rack that provides a computing or storage capacities.
The *service_type* attribute describe whether this ResourceClass is *storage* or
*computing*.

| Attribute     | Type                       | Description                                                  |
|---------------|----------------------------|--------------------------------------------------------------|
| service_type  | String                     | Type of service this class will provide Compute or Storage   |
| flavors       | Array(Struct(Flavor))      | List of Flavor definitions and maximum amount of supported machines for this Flavor type|
| racks         | Collection                 | Collection  of Rack resources available for this class       |

#### ResourceClass example JSON serialization

```json
{
  "id"           : "/resource_classes/1",
  "name"         : "m1",
  "service_type" : "compute",
  "flavors"      : [
                      { "name" : "x-large",
                        "count": 8,
                        "capacities" : [
                          { "name": "cpu",
                            "value" : "4",
                            "unit" : "count" },
                          { "name": "memory",
                            "value" : "8192",
                            "unit" : "MiB" },
                          { "name": "storage",
                            "value" : "1024",
                            "unit" : "GiB" }
                        ]
                      },
                      { "name" : "medium",
                        "count": 16,
                        "capacities" : [
                          { "name": "cpu",
                            "value" : "2",
                            "unit" : "count" },
                          { "name": "memory",
                            "value" : "4096",
                            "unit" : "MiB" },
                          { "name": "storage",
                            "value" : "1024",
                            "unit" : "GiB" }
                        ]
                      }
                   ],
  "racks"   : [
                {
                  "id":1,
                  "links":[
                            { "href":"http://0.0.0.0:6385/v1/rack/1",
                              "rel":"self"
                            }
                          ]
                }
              ]
}
```
[back to top](#index)
<hr/>


## Flavor
<a name="flavor"></a>

Flavor is an available hardware configuration for a server and is defined by
an array of capacities. Each capacity defines a particular aspect of the
hardware configuration with a fixed value, such as memory, cpu, storage,
network or any other relevant hardware configuration information.

A Flavor only exists within the context of a specific ResourceClass. That is,
a Flavor cannot be referenced, retrieved, created, deleted or updated as a
stand-alone resource. All operations on Flavor are performed for a specific
ResourceClass.

| Attribute         | Type                        | Description                                                  |
|-------------------|-----------------------------|--------------------------------------------------------------|
| capacities        | Array(Capacity)             | An array of capacity definitions used by this flavor  |

#### Flavor example JSON serialization

```json
{
  "id"                 : "/resource_class/1/flavors/123",
  "name"               : "micro",
  "capacities"  : [
    {
       "name"  : "cpu",
       "value" : "1",
       "unit"  : "count"
    },
    {
       "name"  : "memory",
       "value" : "1024",
       "unit"  : "MB"
    },
    {
       "name"  : "storage",
       "value" : "5",
       "unit"  : "GB"
    }
  ]
}
```

[back to top](#index)
<hr/>

## Capacity
<a name="capacity"></a>
This model is used to provide the fixed values for the Flavor model and the
aggregate capacity values of all Nodes in a given Rack.

The Capacity model does not have any ID because it is an abstraction model rather
than a realized resource.

| Attribute  | Type                  | Description                                                     |
|------------|-----------------------|-----------------------------------------------------------------|
| name       | String                | A name of the capacity, eg. 'cpu', 'memory', 'storage'          |
| value      | String                | A capacity value, eg. '1024'                                    |
| unit       | String                | Unit used for the value                                         |

#### Capacity example JSON serialization

```json
{
  "name"  : "cpu",
  "value" : "6",
  "unit"  : "count"
}
```

```json
{
  "name"  : "memory",
  "value" : "1024",
  "unit"  : "GB"
}
```

[back to top](#index)
<hr/>

## Rack
<a name="rack"></a>
A Rack represents a grouping of Node resources, assigned to a given
class as a single unit. Each Rack has a total number of slots available for
Nodes, represented by the `slots` attribute. A Rack references the ResourceClass
to which it belongs to as well as an array of references to the Node resources
that the Rack is comprised of. Finally, each Rack resource contains an array
of references to Capacity resources that represent the aggregate capacity
of the nodes making up this Rack.

| Attribute       | Type                     | Description                                                                |
|-----------------|--------------------------|----------------------------------------------------------------------------|
| slots           | String                   | Number of slots that physical rack chassis has. Used for capacity planning |
| resource_class  | Ref(ResourceClass))      | Reference to a ResourceClass current Rack belongs to                       |
| capacities      | Array(Capacity)          | Aggregate Capacities of the nodes that this Rack is comprised of           |
| nodes           | Collection               | Collection of the Nodes that rack contains                                 |
| subnet          | String                   | A network subnet where the Rack belongs to (192.168.1.0/24) (CIDR format)  |
| location        | String                   | Identifier for the physical location of the Rack in the datacenter         |
| status          | String                   | Current status of the Rack, e.g. 'Provisioned'

#### Rack example JSON serialization

```json
{
  "id"              : "/racks/1",
  "name"            : "Dell001",
  "slots"           : "30",
  "subnet"          : "192.168.1.0/24",
  "location"        : "East1",
  "resource_class"  : { "href" : "/resource_classes/1" },
  "capacities" : [
    {
       "name"  : "total_cpu",
       "value" : "12",
       "unit"  : "count"
    },
    {
       "name"  : "total_memory",
       "value" : "3072",
       "unit"  : "MB"
    }
  ],
  "nodes"      : [
                   { "id": "123" },
                   { "id": "345"}
                 ]
}
```

[back to top](#index)
<hr/>

## Node
<a name="node"></a>
A Node represents a single physical compute unit. Each Node includes a
reference to the Rack resource that it is assigned to via the `rack`
attribute. Each node has a `baremetal_node` attribute which references the
physical machine as represented within the Ironic API; this will allow
discovery of the Nodes compute, memory and storage capacities as well as
other relevant attributes such as its MAC address.

| Attribute        | Type                     | Description                                             |
|------------------|--------------------------|---------------------------------------------------------|
| rack             | Ref(Rack)                | A reference to the Rack where Node is located           |
| baremetal_node   | URL                      | A reference to Baremetal API that contains Node details |
| capacities       | Array(Struct(Capacity))  | Total capacity of the Node (mem, cpu, storage,...)      |
| mac_address      | String                   | MAC address of the network interface attached to Node   |
| ip_address       | String                   | IP address of the Node network interface (if available) |
| driver           | String                   | Ironic deployment driver (PXE, etc...)                  |
| power_driver     | Struct                   | Ironic power driver and properties (IPMI username, etc.)|

TBD: Is not clear how much attrs we need to include in this model.

#### Node example JSON serialization

```json
{
  "id"           : "/nodes/1",
  "name"         : "dell-per-601-1",
  "rack"         : { "href" : "/racks/1" },
  "capacities" : [
    {
       "name"  : "cpu",
       "value" : "6",
       "unit"  : "count"
    },
    {
       "name"  : "memory",
       "value" : "8192",
       "unit"  : "MB"
    }
  ],
  "baremetal_node"   : { "href" : "http://server/nodes/123" },
  "mac_address"   : "00:B0:D0:86:BB:F7",
  "ip_address"    : "192.168.1.2",
  "deploy_driver" : "pxe",
  "power_driver"  : {
    "name"      : "ipmi",
    "username"  : "root",
    "password"  : "calvin"
  }
}
```
[back to top](#index)
