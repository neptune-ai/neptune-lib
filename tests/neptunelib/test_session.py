import unittest

from mock import MagicMock, patch

from neptunelib.project import Project
from neptunelib.session import Session
from tests.neptunelib.api_objects_factory import a_project

API_TOKEN = 'eyJhcGlfYWRkcmVzcyI6Imh0dHBzOi8vYXBwLnN0YWdlLm5lcHR1bmUubWwiLCJ' \
            'hcGlfa2V5IjoiOTJhNzhiOWQtZTc3Ni00ODlhLWI5YzEtNzRkYmI1ZGVkMzAyIn0='


@patch('neptunelib.client.SwaggerClient.from_url', MagicMock())
@patch('neptunelib.client.NeptuneAuthenticator', MagicMock())
class TestSession(unittest.TestCase):
    # pylint: disable=protected-access,no-member

    @patch('neptunelib.credentials.os.getenv', return_value=API_TOKEN)
    def test_should_take_default_credentials_from_env(self, _):
        # when
        session = Session()

        # then
        self.assertEqual(API_TOKEN, session.credentials.api_token)

    @patch('neptunelib.credentials.os.getenv', return_value=API_TOKEN)
    def test_should_accept_given_credentials(self, os_getenv):
        # given
        credentials = MagicMock()

        # when
        session = Session(credentials)

        # then
        self.assertEqual(credentials, session.credentials)

        # and
        os_getenv.assert_not_called()

    @patch('neptunelib.session.Client')
    def test_get_projects_with_given_namespace(self, _):
        # given
        credentials = MagicMock()
        credentials.namespace = 'default'

        # and
        api_projects = [a_project(), a_project()]

        # and
        session = Session(credentials)
        session._client.get_projects.return_value = api_projects

        # and
        custom_namespace = 'custom_namespace'

        # when
        projects = session.get_projects(custom_namespace)

        # then
        expected_projects = {
            custom_namespace + '/' + p.name:
                Project(session._client, p.id, custom_namespace, p.name) for p in api_projects
        }
        self.assertEqual(expected_projects, projects)

        # and
        session._client.get_projects.assert_called_with(custom_namespace)


if __name__ == '__main__':
    unittest.main()
