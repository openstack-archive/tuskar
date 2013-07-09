# OpenStack Management API Draft

## ERD diagram:

* 05-30-2013: [version 1.0](./img/model_v1.jpg)
* 06-03-2013: [version 2.0](./img/model_v2.jpg)
* 06-04-2013: [version 3.0](./img/model_v3.jpg)

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

## ResourceClass

The ResourceClass describes the list of instance types (flavors) and the
array of references to the Rack that provides a computing or storage capacities.
The *service_type* attribute describe whether this ResourceClass is *storage* or
*computing*.

| Attribute     | Type                       | Description                                                  |
|---------------|----------------------------|--------------------------------------------------------------|
| service_type  | String                     | Type of service this class will provide Compute or Storage   |
| flavors       | Array(Struct(Ref(Flavor))) | List of references to flavors and maximum amount of machines |
| racks         | Collection                 | Collection  of Rack resources available for this class       |

#### Struct(Ref(Flavor))

Just an explanation of how the Struct should looks like:

| Attribute     | Type                       | Description                                                                 |
|---------------|----------------------------|-----------------------------------------------------------------------------|
| flavor        | Ref(Flavor)                | A reference to the Flavor                                                   |
| count         | String                     | A maximum number of VM  that could be started with this flavor on one Host in this class |

#### ResourceClass example JSON serialization

```json
{
  "id"           : "/resource_classes/1",
  "name"         : "m1",
  "service_type" : "compute",
  "flavors"      : {
    "count"      : "2",
    "resources"  : [
      { "href" : "/flavors/123", "count" : "256" },
      { "href" : "/flavors/456", "count" : "64"  }
    ],
    "actions"    : [
      {
        "rel"    : "add",
        "method" : "put",
        "url"    : "/resource_class/1/flavors"
      }
    ]
  },
  "racks"   : {
    "count"   : "2",
    "resources" : [
      { "href" : "/racks/1" },
      { "href" : "/racks/2" },
    ],
    "actions" : [
      {
        "rel"    : "add",
        "method" : "put",
        "url"    : "/resource_class/1/racks"
      }
    ]
  }
}
```

## Flavor

Flavor is an available hardware configuration for a server. Each flavor has a
unique combination of different capacities.  Each capacity defines the hardware
property with fixed value. Capacity could be a memory, cpu, storage, network or
other relevant hardware configuration information.

| Attribute         | Type                        | Description                                                  |
|-------------------|-----------------------------|--------------------------------------------------------------|
| capacities        | Array(Struct(Capacity))        | A list with references to capacities used by this flavor  |

#### Flavor example JSON serialization

```json
{
  "id"                 : "/flavors/123",
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

## Capacity

This model is used to provide the fixed values for the Flavor model and the
aggregate capacity values of all Hosts in a given Rack.

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

## Rack

A Rack represents a grouping of Host resources, assigned to a given
class as a single unit. Each Rack has a total number of slots available for
Hosts, represented by the `slots` attribute. A Rack references the ResourceClass
to which it belongs to as well as an array of references to the Host resources
that the Rack is comprised of. Finally, each Rack resource contains an array
of references to Capacity resources that represent the aggregate capacity
of the hosts making up this Rack.

| Attribute       | Type                     | Description                                                                |
|-----------------|--------------------------|----------------------------------------------------------------------------|
| slots           | String                   | Number of slots that physical rack chassis has. Used for capacity planning |
| resource_class  | Ref(ResourceClass))      | Reference to a ResourceClass current Rack belongs to                       |
| capacities      | Array(Struct(Capacity))  | Aggregate Capacities of the hosts that this Rack is comprised of           |
| hosts           | Collection               | Collection of the Hosts (nodes) that rack contains                         |
| subnet          | String                   | A network subnet where the Rack belongs to (192.168.1.0/24) (CIDR format)  |
| region          | Ref(Region)??            | A reference to the Region (to be defined)                                  |

#### Rack example JSON serialization

```json
{
  "id"              : "/racks/1",
  "name"            : "Dell001",
  "slots"           : "30",
  "subnet"          : "192.168.1.0/24",
  "region"          : { "href" : "/regions/1" },
  "resource_class"  : { "href" : "/resource_class/1" },
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
  "hosts"           : {
    "count"     : "3",
    "resources" : [
      { "href" : "/hosts/1" },
      { "href" : "/hosts/2" },
      { "href" : "/hosts/3" }
    ],
    "actions"  : [
      {
        "rel"    : "add",
        "method" : "put",
        "url"    : "/racks"
      }
    ]
  }
}
```

## Host

A Host represents a single physical compute unit. Each Host includes a
reference to the Rack resource that it is assigned to via the `rack`
attribute. Each host has a `ironic_node` attribute which references the
physical machine as represented within the Ironic API; this will allow
discovery of the Hosts compute, memory and storage capacities as well as
other relevant attributes such as its MAC address.

| Attribute        | Type                     | Description                                             |
|------------------|--------------------------|---------------------------------------------------------|
| rack             | Ref(Rack)                | A reference to the Rack where Host is located           |
| ironic_node      | URL                      | A reference to Ironic API that contains Host details    |
| capacities       | Array(Struct(Capacity))  | Total capacity of the Host (mem, cpu, storage,...)      |
| mac_address      | String                   | MAC address of the network interface attached to Host   |
| ip_address       | String                   | IP address of the Host network interface (if available) |
| driver           | String                   | Ironic deployment driver (PXE, etc...)                  |
| power_driver     | Struct                   | Ironic power driver and properties (IPMI username, etc.)|

TBD: Is not clear how much attrs we need to include in this model.

#### Host example JSON serialization

```json
{
  "id"           : "/hosts/1",
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
  "ironic_node"   : { "href" : "http://server/hosts/123" },
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
