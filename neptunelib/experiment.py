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

import pandas as pd
from pandas.errors import EmptyDataError

from utils import map_values, align_channels_on_x


class Experiment(object):
    def __init__(self, client, leaderboard_entry):
        self._client = client
        self._leaderboard_entry = leaderboard_entry

    # TODO: posortowanie kolumn

    @property
    def id(self):
        return self._leaderboard_entry.id

    @property
    def system_properties(self):
        """
        Retrieve system properties like owner, times of creation and completion, worker type, etc.
        Note, that the list of supported system properties changes over time.

        :return: A `pandas.DataFrame` containing a column for every property.
        """
        return self._simple_dict_to_dataframe(self._leaderboard_entry.system_properties)

    @property
    def channels(self):
        """
        Retrieve all channel names along with their types for this experiment.

        :return: A dictionary mapping a channel name to its type.
        """
        return dict(
            (ch.name, ch.type) for ch in self._leaderboard_entry.channels
        )

    @property
    def parameters(self):
        """
        Retrieve parameters for this experiment.

        :return: A `pandas.DataFrame` containing a column for every parameter.
        """
        return self._simple_dict_to_dataframe(self._leaderboard_entry.parameters)

    @property
    def properties(self):
        """
        Retrieve user-defined properties for this experiment.

        :return: A `pandas.DataFrame` containing a column for every property.
        """
        return self._simple_dict_to_dataframe(self._leaderboard_entry.properties)

    def get_hardware_utilization(self):
        """
        Retrieve RAM, CPU and GPU utilization throughout the experiment.

        The returned DataFrame contains 2 columns (x_*, y_*) for each of: RAM, CPU and each GPU.
        The x_ column contains the time (in milliseconds) from the experiment start,
        while the y_ column contains the value of the appropriate metric.

        RAM and GPU memory usage is returned in gigabytes.
        CPU and GPU utilization is returned as a percentage (0-100).

        E.g. For an experiment using a single GPU, this method will return a DataFrame
        of the following columns:

        x_ram, y_ram, x_cpu, y_cpu, x_gpu_util_0, y_gpu_util_0, x_gpu_mem_0, y_gpu_mem_0

        The following values denote that after 3 seconds, the experiment used 16.7 GB of RAM.
        x_ram, y_ram = 3000, 16.7

        The returned DataFrame may contain NaNs if one of the metrics has more values than others.

        :return: A `pandas.DataFrame` containing the hardware utilization metrics throughout the experiment.
        """
        metrics_csv = self._client.get_metrics_csv(self._leaderboard_entry.internal_id)
        try:
            return pd.read_csv(metrics_csv)
        except EmptyDataError:
            return pd.DataFrame()

    def get_numeric_channels_values(self, *channel_names, align_on_x=True):
        """
        Retrieve values of specified numeric channels.

        The returned DataFrame contains 2 columns (x_*, y_*) for every requested channel.
        The x_ and y_ columns contain the X and Y coordinate of each point in a channel respectively.

        E.g. get_numeric_channels_values('loss', 'auc') will return a DataFrame
        of the following structure:

        x_loss, y_loss, x_auc, y_auc

        The returned DataFrame may contain NaNs if one of the channels has more values than others.

        :param channel_names: Names of the channels to retrieve values for.
        :param aligh_x: Bool whether to join all `x_` channels into one `x` channel.
        :return: A `pandas.DataFrame` containing the values for the requested channels.
        """

        channels_data = {}
        for channel_name in channel_names:
            channel_id = self._leaderboard_entry.channels_dict_by_name[channel_name].id
            try:
                channels_data[channel_name] = pd.read_csv(
                    self._client.get_channel_points_csv(self._leaderboard_entry.internal_id, channel_id),
                    header=None,
                    names=['x_{}'.format(channel_name), 'y_{}'.format(channel_name)]
                )
            except EmptyDataError:
                channels_data[channel_name] = pd.DataFrame(
                    columns=['x_{}'.format(channel_name), 'y_{}'.format(channel_name)]
                )

        if align_on_x:
            return align_channels_on_x(pd.concat(channels_data.values(), axis=1, sort=False))
        else:
            return pd.concat(channels_data.values(), axis=1, sort=False)

    def __str__(self):
        return 'Experiment({})'.format(self.id)

    def __repr__(self):
        return str(self)

    def __eq__(self, o):
        return self.__dict__ == o.__dict__

    def __ne__(self, o):
        return not self.__eq__(o)

    @staticmethod
    def _simple_dict_to_dataframe(d):
        return pd.DataFrame.from_dict(map_values(lambda x: [x], d))
