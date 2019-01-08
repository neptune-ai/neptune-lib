#
# Copyright (c) 2019, Neptune Labs Sp. z o.o.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from neptunelib.client import Client
from neptunelib.credentials import Credentials
from neptunelib.project import Project


class Session(object):
    def __init__(self, credentials=None):
        """
        :param credentials: `Credentials` object for authenticating your calls to Neptune API.
        """
        self.credentials = credentials or Credentials.from_env()
        self._client = Client(self.credentials.api_address, self.credentials.api_token)

    def get_projects(self, namespace):
        """
        Retrieve projects from given namespace, that our available using given credentials.

        :param namespace: The default namespace is the one you declared when creating your API token.
        :return: A dictionary: project_name -> Project object
        """
        projects = [Project(self._client, p.id, namespace, p.name) for p in self._client.get_projects(namespace)]
        return dict((p.full_id, p) for p in projects)
