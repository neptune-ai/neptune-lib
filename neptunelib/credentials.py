import base64
import json
import os

from neptunelib.exceptions import InvalidApiToken


class Credentials(object):
    API_TOKEN_ENV_NAME = 'NEPTUNE_API_TOKEN'

    @classmethod
    def from_env(cls):
        """
        This is the preferred, more secure, method of building the `Credentials` object.
        This method expects Neptune API key to be present in the `NEPTUNE_API_TOKEN`
        environment variable.

        You can retrieve a valid Neptune API key with `neptune account api-key get`.

        When running your code in Neptune's Jupyter notebook, or via `neptune send`,
        this variable is set to a valid API key.

        :return: A `Credentials` object.
        """

        api_token = os.getenv(cls.API_TOKEN_ENV_NAME)
        return cls(api_token)

    # TODO: API token should contain (url, api_key and namespace)
    def __init__(self, api_token):
        """
        A constructor allowing for passing Neptune API key explicitly.
        Use this method only if you're certain that your code will stay private.
        Otherwise, refer to the more secure `from_env` method.

        :param api_token: This is a secret API key that you can retrieve with `neptune account api-token get <org>`.
        """
        self.api_token = api_token

    @property
    def api_address(self):
        """
        :return: The address of the Neptune API associated with these credentials.
        """
        return self._api_token_to_dict(self.api_token)['api_address']

    @staticmethod
    def _api_token_to_dict(api_token):
        try:
            return json.loads(base64.b64decode(api_token.encode()))
        except Exception:
            raise InvalidApiToken("Failed to deserialize API token: {}".format(api_token))
