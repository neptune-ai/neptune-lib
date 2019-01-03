from typing import Dict

from neptune.client.client import Client
from neptune.lib.credentials import Credentials
from neptune.lib.project import Project


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


def main():
    sample_api_token = "eyJhcGlfYWRkcmVzcyI6Imh0dHBzOi8vYXBwLnN0YWdlLm5lcHR1bmUubWwiLCJhcGlfa2V5" \
                       "IjoiOTJhNzhiOWQtZTc3Ni00ODlhLWI5YzEtNzRkYmI1ZGVkMzAyIn0="
    class FakeCreds(object):
        def __init__(self):
            self.api_address = 'https://app.stage.neptune.ml/api'
            self.api_token = ''

    s = Session(Credentials(sample_api_token))
    # s = Session(FakeCreds())
    print('Session created.\n')

    print('User profile:')
    print(s._client.backend_swagger_client.api.getUserProfile().response().result)

    projects = s.get_projects('hubert3')
    print('Projects: {}\n'.format(projects))

    project = projects['hubert3/sandbox-old']
    members = project.get_members()
    print('Members: {}\n'.format(members))

    experiments = project.get_experiments()
    print('Experiments ({}): {}\n'.format(len(experiments), experiments))

    import pandas as pd
    with pd.option_context('display.max_rows', 10, 'display.max_columns', None, 'display.width', None):
        exp = next(e for e in experiments if e.id == 'SAN-49')
        print('System properties:\n{}\n'.format(exp.system_properties))
        print('Properties:\n{}\n'.format(exp.properties))
        print('Parameters:\n{}\n'.format(exp.parameters))
        print('Channels:\n{}\n'.format(exp.channels))

        leaderboard = project.get_leaderboard()
        print('Leaderboard:\n{}\n'.format(leaderboard))

    with pd.option_context('display.max_rows', 10, 'display.max_columns', None, 'display.width', None):
        channel_values = exp.get_numeric_channels_values('Accuracy training', 'Accuracy validation')
        print('channel values:\n{}\n'.format(channel_values))

    with pd.option_context('display.max_rows', 10, 'display.max_columns', None, 'display.width', None):
        metrics = exp.get_hardware_utilization()
        print('metrics:\n{}\n'.format(metrics))

    print(1)


if __name__ == '__main__':
    main()
