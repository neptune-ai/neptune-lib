from typing import Dict

from neptunelib.client import Client
from neptunelib.credentials import Credentials
from neptunelib.project import Project


class Session(object):
    def __init__(self, credentials: Credentials = Credentials.from_env()):
        """
        :param credentials: `Credentials` object for authenticating your calls to Neptune API.
        """
        self.credentials = credentials
        self._client = Client(credentials.api_address, credentials.api_token)

    def get_projects(self, namespace=None) -> Dict[str, Project]:
        """
        Retrieve projects from given namespace, that our available using given credentials.

        :param namespace: The default namespace is the one you declared when creating your API token.
        :return: A dictionary: project_name -> Project object
        """
        if namespace is None:
            namespace = self.credentials.namespace

        projects = [Project(self._client, p.id, namespace, p.name) for p in self._client.get_projects(namespace)]

        return dict((p.full_id, p) for p in projects)
