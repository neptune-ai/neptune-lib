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

from io import StringIO
import unittest

from mock import MagicMock

from neptunelib.experiment import Experiment


class TestExperiment(unittest.TestCase):

    def test_get_numeric_channels_values(self):
        # when
        client = MagicMock()
        client.get_channel_points_csv.return_value = StringIO(u'\n'.join(['0.3,2.5', '1,2']))

        leaderboard_entry = MagicMock()
        dict_value = MagicMock()
        dict_value.id = 0
        leaderboard_entry.channels_dict_by_name = {'epoch_loss': dict_value}
        leaderboard_entry.internal_id = 0

        # then
        experiment = Experiment(client, leaderboard_entry)
        experiment.get_numeric_channels_values('epoch_loss')


if __name__ == '__main__':
    unittest.main()
