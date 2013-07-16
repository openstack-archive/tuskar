# Server Specific Configurations
server = {
    'port': '6382',
    'host': '0.0.0.0'
}

# Pecan Application Configurations
app = {
    'root': 'tuskar.api.controllers.root.RootController',
    'modules': ['tuskar.api'],
    'static_root': '%(confdir)s/public',
    'template_path': '%(confdir)s/templates',
    'debug': False,
    'enable_acl': False,
}

# Custom Configurations must be in Python dictionary format::
#
# foo = {'bar':'baz'}
#
# All configurations are accessible at::
# pecan.conf
