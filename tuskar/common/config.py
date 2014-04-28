# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# Copyright 2012 Red Hat, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo.config import cfg

from tuskar.common import paths
from tuskar.common import rpc
from tuskar.openstack.common.db.sqlalchemy import session as db_session
from tuskar import version

_DEFAULT_SQL_CONNECTION = 'sqlite:///' + paths.state_path_def('$sqlite_db')


def parse_args(argv, default_config_files=None):
    db_session.set_defaults(sql_connection=_DEFAULT_SQL_CONNECTION,
                            sqlite_db='tuskar.sqlite')
    rpc.set_defaults(control_exchange='tuskar')
    cfg.CONF(argv[1:],
             project='tuskar',
             version=version.version_string(),
             default_config_files=default_config_files)
    rpc.init(cfg.CONF)
