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
