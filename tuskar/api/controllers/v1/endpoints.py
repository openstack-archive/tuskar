import pecan

import tuskar.heat.client


class EndpointsController(pecan.rest.RestController):
    """Controller for the overcloud API endpoints
    """

    @pecan.expose('json')
    def get_all(self):
        heat = tuskar.heat.client.HeatClient()
        outputs = heat.get_stack().outputs

        endpoints = dict()
        for service in outputs:
            endpoints[service['output_key']] = service['output_value']

        return endpoints
