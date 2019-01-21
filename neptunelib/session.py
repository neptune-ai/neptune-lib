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
    """It handles the communication with the Neptune experiment database.

    In order to query Neptune experiment database in any way you have to instantiate this object first.

    Args:
        api_token(str): This is a secret API key that you can retrieve by running 
            `$ neptune account api-token get`.

    Attributes:
        credentials (:obj:`Credentials`): `Credentials` object instance that authenticates your calls to Neptune API.

    Examples:
        Examples should be written in doctest format, and should illustrate how
        to use the function.

        >>> from neptunelib.session import Session
        >>> session = Session(api_token='YOUR_NEPTUNE_API_TOKEN')

        or assuming you have created an environment variable by running:

        `export NEPTUNE_API_TOKEN=YOUR_NEPTUNE_API_TOKEN`

        and simply go:

        >>> session = Session()
    """

    def __init__(self, api_token=None):
        credentials = Credentials(api_token) if api_token else Credentials.from_env()

        self.credentials = credentials
        self._client = Client(self.credentials.api_address, self.credentials.api_token)

    def get_projects(self, namespace):
        """It gets all project and full project names for given namespace

        In order to access experiment data one needs to get a `Project` object first. This method helps you figure out
           what are the available projects and access the project of interest.
           You can list both your private and public projects.
           You can also access all the public projects that belong to any user or organization,
           as long as you know what is their namespace.

        Args:
            namespace(str): It can either be your organization or user name. You can list all the public projects
                for any organization or user you want as long as you know their namespace.

        Returns:
            dict: Dictionary of NAMESPACE/PROJECT_NAME: `Project` object pairs that contains all the projects that
                belong to the selected namespace.

        Examples:
            First, you need to create a Session instance:

            >>> from neptunelib.session import Session
            >>> session = Session()

            Now, you can list all the projects available for a selected namespace. You can use `YOUR_NAMESPACE` which
                is your organization or user name. You can also list public projects created by other organizations.
                For example you can use the `neptune-ml` namespace.

            >>> session.get_projects('neptune-ml')

            {'neptune-ml/neptune-tutorials': Project(neptune-ml/neptune-tutorials),
             'neptune-ml/Sandbox': Project(neptune-ml/Sandbox),
             'neptune-ml/Toxic-Comment-Classification-Challenge':
                 Project(neptune-ml/Toxic-Comment-Classification-Challenge),
             'neptune-ml/Home-Credit-Default-Risk': Project(neptune-ml/Home-Credit-Default-Risk),
             'neptune-ml/Santander-Value-Prediction-Challenge':
                 Project(neptune-ml/Santander-Value-Prediction-Challenge),
             'neptune-ml/Mapping-Challenge': Project(neptune-ml/Mapping-Challenge),
             'neptune-ml/Ships': Project(neptune-ml/Ships),
             'neptune-ml/human-protein-atlas': Project(neptune-ml/human-protein-atlas),
             'neptune-ml/Salt-Detection': Project(neptune-ml/Salt-Detection),
             'neptune-ml/GStore-Customer-Revenue-Prediction':
                 Project(neptune-ml/GStore-Customer-Revenue-Prediction),
             'neptune-ml/Data-Science-Bowl-2018': Project(neptune-ml/Data-Science-Bowl-2018),
             'neptune-ml/Google-AI-Object-Detection-Challenge':
                 Project(neptune-ml/Google-AI-Object-Detection-Challenge),
             'neptune-ml/piotr-lusakowski-testy': Project(neptune-ml/piotr-lusakowski-testy)}
        """

        projects = [Project(self._client, p.id, namespace, p.name) for p in self._client.get_projects(namespace)]
        return dict((p.full_id, p) for p in projects)
