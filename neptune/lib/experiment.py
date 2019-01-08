from typing import Dict
import pandas as pd

from neptune.utils import map_values


class Experiment(object):
    def __init__(self, client, leaderboard_entry):
        self._client = client
        self._leaderboard_entry = leaderboard_entry

    # TODO: posortowanie kolumn

    @property
    def id(self):
        return self._leaderboard_entry.id

    @property
    def system_properties(self) -> pd.DataFrame:
        """
        Retrieve system properties like owner, times of creation and completion, worker type, etc.
        Note, that the list of supported system properties changes over time.

        :return: A `pandas.DataFrame` containing a column for every property.
        """
        return self._simple_dict_to_dataframe(self._leaderboard_entry.system_properties)

    @property
    def channels(self) -> Dict[str, str]:
        """
        Retrieve all channel names along with their types for this experiment.

        :return: A dictionary mapping a channel name to its type.
        """
        return dict(
            (ch.name, ch.type) for ch in self._leaderboard_entry.channels
        )

    @property
    def parameters(self) -> pd.DataFrame:
        """
        Retrieve parameters for this experiment.

        :return: A `pandas.DataFrame` containing a column for every parameter.
        """
        return self._simple_dict_to_dataframe(self._leaderboard_entry.parameters)

    @property
    def properties(self) -> pd.DataFrame:
        """
        Retrieve user-defined properties for this experiment.

        :return: A `pandas.DataFrame` containing a column for every property.
        """
        return self._simple_dict_to_dataframe(self._leaderboard_entry.properties)

    def get_hardware_utilization(self) -> pd.DataFrame:
        """
        Retrieve RAM, CPU and GPU utilization throughout the experiment.

        The returned DataFrame contains 2 columns (x_*, y_*) for each of: RAM, CPU and each GPU.
        The x_ column contains the time (in milliseconds) from the experiment start,
        while the y_ column contains the value of the appropriate metric.

        RAM and GPU memory usage is returned in gigabytes.
        CPU and GPU utilization is returned as a percentage (0-100).

        E.g. For an experiment using a single GPU, this method will return a DataFrame
        of the following columns:

        x_ram, y_ram, x_cpu, y_cpu, x_gpu_util_1, y_gpu_util_1, x_gpu_mem_1, y_gpu_mem_1

        The following values denote that after 3 seconds, the experiment used 16.7 GB of RAM.
        x_ram, y_ram = 3000, 16.7

        The returned DataFrame may contain NaNs if one of the metrics has more values than others.

        :return: A `pandas.DataFrame` containing the hardware utilization metrics throughout the experiment.
        """
        pass

    def get_numeric_channels_values(self, *channel_names: str) -> pd.DataFrame:
        """
        Retrieve values of specified numeric channels.

        The returned DataFrame contains 2 columns (x_*, y_*) for every requested channel.
        The x_ and y_ columns contain the X and Y coordinate of each point in a channel respectively.

        E.g. get_numeric_channels_values('loss', 'auc') will return a DataFrame
        of the following structure:

        x_loss, y_loss, x_auc, y_auc

        The returned DataFrame may contain NaNs if one of the channels has more values than others.

        :param channel_names: Names of the channels to retrieve values for.
        :return: A `pandas.DataFrame` containing the values for the requested channels.
        """

        data = {}
        for channel_name in channel_names:
            channel_id = self._leaderboard_entry.channels_dict_by_name[channel_name].id
            points = self._client.get_channel_points(self._leaderboard_entry.internal_id, channel_id)
            data['x_{}'.format(channel_name)] = pd.Series(points.xs)
            data['y_{}'.format(channel_name)] = pd.Series(points.numeric_ys)

        return pd.DataFrame.from_dict(data)

    def __str__(self):
        return 'Experiment({})'.format(self.id)

    def __repr__(self):
        return str(self)

    @staticmethod
    def _simple_dict_to_dataframe(d):
        return pd.DataFrame.from_dict(map_values(lambda x: [x], d))
