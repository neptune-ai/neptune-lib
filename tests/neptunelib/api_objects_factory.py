from mock import MagicMock

from tests.neptunelib.random_utils import a_string, a_uuid_string


def a_project():
    project = MagicMock()
    project.id = a_uuid_string()
    project.name = a_string()
    return project
