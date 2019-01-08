from bravado.client import SwaggerClient
from bravado_core.formatter import SwaggerFormat

from neptune.model import LeaderboardEntry, Points


class Client(object):
    def __init__(self, api_address, api_token):
        self.api_address = api_address
        self.api_token = api_token

        self.backend_swagger_client = SwaggerClient.from_url(
            '{}/backend/swagger.json'.format(self.api_address),
            config=dict(
                validate_swagger_spec=False,
                formats=[uuid_format]))

        self.leaderboard_swagger_client = SwaggerClient.from_url(
            '{}/leaderboard/swagger.json'.format(self.api_address),
            config=dict(
                validate_swagger_spec=False,
                validate_responses=False,  # TODO!!!
                formats=[uuid_format]))
        # TODO: !!!
        self.leaderboard_swagger_client.swagger_spec.api_url = 'https://app.neptune.ml'

    def get_projects(self, namespace):
        r = self.backend_swagger_client.api.listProjectsInOrganization(
            organizationName=namespace
        ).response()
        return r.result.entries

    def get_project_members(self, namespace, project_name):
        r = self.backend_swagger_client.api.listProjectMembers(
            organizationName=namespace, projectName=project_name
        ).response()

        return r.result

    def get_leaderboard_entries(self, namespace, project_name):
        def get_portion(limit, offset):
            return self.leaderboard_swagger_client.api.projectLeaderboard(
                organizationName=namespace, projectName=project_name,
                limit=limit, offset=offset
            ).response().result.entries

        return [LeaderboardEntry(e) for e in self._get_all_items(get_portion, step=100)]

    def get_channel_points(self, experiment_internal_id, channel_internal_id):
        def get_portion(limit, offset):
            return self.backend_swagger_client.api.getChannelValues(
                experimentId=experiment_internal_id, channelId=channel_internal_id,
                limit=limit, offset=offset
            ).response().result.values

        return Points(self._get_all_items(get_portion, step=1000))

    @staticmethod
    def _get_all_items(get_portion, step):
        items = []

        previous_items = None
        while previous_items is None or len(previous_items) >= step:
            previous_items = get_portion(limit=step, offset=len(items))
            items += previous_items

        return items


uuid_format = SwaggerFormat(
    format='uuid',
    to_python=lambda x: x,
    to_wire=lambda x: x,
    validate=lambda x: None,
    description=''
)
