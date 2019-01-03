from io import StringIO

from bravado.client import SwaggerClient
from bravado.requests_client import Authenticator
from bravado.requests_client import RequestsClient
from bravado_core.formatter import SwaggerFormat
from requests.auth import AuthBase

from neptune.model import LeaderboardEntry


class OAuthNoRefreshAuth(AuthBase):
    # TODO add in-memory refresh-before-request mechanism

    def __init__(self, access_token, refresh_token):
        self.access_token = access_token
        self.refresh_token = refresh_token

    def __eq__(self, other):
        return all([
            self.access_token == getattr(other, 'access_token', None),
            self.refresh_token == getattr(other, 'refresh_token', None)
        ])

    def __ne__(self, other):
        return not self == other

    def __call__(self, r):
        r.headers['Authorization'] = "Bearer {}".format(self.access_token)
        return r


class NeptuneAuthenticator(Authenticator):

    def __init__(self):
        super(NeptuneAuthenticator, self).__init__("")
        self.auth = None

    def set_auth(self, auth):
        self.auth = auth

    def matches(self, url):
        return True if self.auth else False

    def apply(self, request):
        request.auth = self.auth
        return request


class Client(object):
    def __init__(self, api_address, api_token):
        self.api_address = api_address
        self.api_token = api_token

        http_client = RequestsClient()
        http_client.authenticator = NeptuneAuthenticator()

        self.backend_swagger_client = SwaggerClient.from_url(
            '{}/api/backend/swagger.json'.format(self.api_address),
            config=dict(
                validate_swagger_spec=False,
                formats=[uuid_format]),
            http_client=http_client)

        if api_token:
            r = self.backend_swagger_client.api.exchangeApiToken(X_Neptune_Api_Token=api_token).response().result
            http_client.authenticator.set_auth(OAuthNoRefreshAuth(r.accessToken, r.refreshToken))

        self.leaderboard_swagger_client = SwaggerClient.from_url(
            '{}/api/leaderboard/swagger.json'.format(self.api_address),
            config=dict(
                validate_swagger_spec=False,
                validate_responses=False,  # TODO!!!
                formats=[uuid_format]),
            http_client=http_client)

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
            return self.leaderboard_swagger_client.api.getLeaderboard(
                projectIdentifier="{}/{}".format(namespace, project_name),
                limit=limit, offset=offset
            ).response().result.entries

        return [LeaderboardEntry(e) for e in self._get_all_items(get_portion, step=100)]

    def get_channel_points_csv(self, experiment_internal_id, channel_internal_id):
        csv = StringIO()
        csv.write(
            self.backend_swagger_client.api.getChannelValuesCSV(
                experimentId=experiment_internal_id, channelId=channel_internal_id
            ).response().incoming_response.text
        )
        csv.seek(0)
        return csv

    def get_metrics_csv(self, experiment_internal_id):
        csv = StringIO()
        csv.write(
            self.backend_swagger_client.api.getSystemMetricsCSV(
                experimentId=experiment_internal_id
            ).response().incoming_response.text
        )
        csv.seek(0)
        return csv

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
