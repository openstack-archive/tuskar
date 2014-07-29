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


class StorageException(Exception):
    pass


class UnknownUUID(StorageException):
    """Raised when an object with the given UUID can't be found."""


class UnknownName(StorageException):
    """Raised when an object with the given Name can't be found."""


class UnknownVersion(StorageException):
    """Raised when an object with the given Version can't be found."""


class NameAlreadyUsed(StorageException):
    """Raised when creating an object with a name that is already in use."""
