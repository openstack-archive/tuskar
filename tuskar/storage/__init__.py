# -*- encoding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from oslo.config import cfg

from tuskar.openstack.common import log as logging

heat_opts = [
    cfg.StrOpt(
        'driver',
        default='tuskar.storage.drivers.sqlalchemy.SQLAlchemyDriver',
        help=('Storage driver to store Deployment Plans and Heat '
              'Orchestration Templates')
    )
]

CONF = cfg.CONF
CONF.register_opts(heat_opts, group='storage')
LOG = logging.getLogger(__name__)


def _import_class(dotted_path):
    module, object_ = dotted_path.rsplit('.', 1)
    mod = __import__(module, fromlist=[object_, ])
    return getattr(mod, object_)


def get_driver(store_class):
    """Given the store class, look up the configuration and load the storage
    driver being used for that store.

    :param store_class: Store instance that is requesting a driver.
    :type  store_class: tuskar.storage.stores._BaseStore

    :return: Instance of the driver
    :rtype:  tuskar.storage.drivers.base.BaseDriver
    """

    # TODO(dmatthew): Currently this only loads one fixed driver, we need to
    #                 either change the function signature or add more config
    #                 options. Depending which makes most sense.
    driver_path = CONF.storage['driver']
    Driver = _import_class(driver_path)
    return Driver()
