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
        """ The address of the Neptune API associated with these credentials.
        
        Returns:
            str: URL address of the Neptune instance
        
        Example:
            >>> from neptunelib.credentials import Credentials
            >>> credentials=Credentials.from_env()
            >>> credentials.api_address
            'https://app.neptune.ml'
        """
        return self._api_token_to_dict(self.api_token)['api_address']

    @staticmethod
    def _api_token_to_dict(api_token):
        try:
            return json.loads(base64.b64decode(api_token.encode()).decode("utf-8"))
        except Exception:
            raise InvalidApiToken("Failed to deserialize API token: {}".format(api_token))
