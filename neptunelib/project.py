from typing import List, Optional, Union

import pandas as pd

from neptunelib.experiment import Experiment
from neptunelib.utils import as_list, map_keys

OptionalStrOrStrList = Union[None, str, List[str]]


class Project(object):
    def __init__(self, client, internal_id, namespace, name):
        self.client = client
        self.internal_id = internal_id
        self.namespace = namespace
        self.name = name

    def get_members(self) -> List[str]:
        """
        Retrieve a list of project members.

        :return: A list of usernames of project members.
        """
        return self.client.get_project_members(self.namespace, self.name)

    def get_experiments(self, id=None, group=None, state=None, owner=None, tag=None, min_running_time=None):
        """
        Retrieve a list of experiments matching the specified criteria.
        All of the parameters of this method are optional, each of them specifies a single criterion.

        Only experiments matching all of the criteria will be returned.

        If a specific criterion accepts a list (like `state`), experiments matching any element of the list
        match this criterion.

        E.g. get_experiments(state=['Running', 'Aborted'], owner=['UserA', 'UserB]) will return experiments
        created by UserA or UserB that are Running or Aborted at the time of request.

        :param id: An ID or list of experiment IDs (e.g. 'SAN-1' or ['SAN-1', 'SAN-2'])
        :param group: A group or list of groups the returned experiments have to be in.
                    E.g. 'SAN-GRP-1', ['SAN-GRP-1', 'SAN-GRP-2']
        :param state: A state or list of experiment states.
                    E.g. 'Succeeded' or ['Succeeded', 'Preempted']
                    Possible states: 'Creating', 'Waiting', 'Initializing', 'Running',
                        'Cleaning', 'Crashed', 'Failed', 'Aborted', 'Preempted', 'Succeeded'
        :param owner: The owner or list of owners of the experiments. This parameter expects usernames.
        :param tag: A tag or a list of experiment tags. E.g. 'solution-1' or ['solution-1', 'solution-2'].
        :param min_running_time: Minimum running time of an experiment in seconds.
        """
        leaderboard_entries = self._fetch_leaderboard(id, group, state, owner, tag, min_running_time)
        return [
            Experiment(self.client, entry) for entry in leaderboard_entries
        ]

    def get_leaderboard(self, id=None, group=None, state=None, owner=None, tag=None, min_running_time=None):
        """
        Retrieve experiments matching the specified criteria and present them in a form of a DataFrame
        resembling Neptune's leaderboard.

        The returned DataFrame contains columns for all system properties,
        numeric and text channels, user-defined properties and parameters defined
        in the selected experiments (not across the entire project).

        Every row in this DataFrame represents a single experiment. As such, some columns may be empty,
        since experiments define various channels, properties, etc.

        For each channel at most one (the last one) value is returned per experiment.
        Text values are trimmed to 255 characters.

        All of the parameters of this method are optional, each of them specifies a single criterion.

        Only experiments matching all of the criteria will be returned.

        If a specific criterion accepts a list (like `state`), experiments matching any element of the list
        match this criterion.

        E.g. get_experiments(state=['Running', 'Aborted'], owner=['UserA', 'UserB]) will return experiments
        created by UserA or UserB that are Running or Aborted at the time of request.

        :param id: An ID or list of experiment IDs (rowo.g. 'SAN-1' or ['SAN-1', 'SAN-2'])
        :param group: A group or list of groups the returned experiments have to be in.
                    E.g. 'SAN-GRP-1', ['SAN-GRP-1', 'SAN-GRP-2']
        :param state: A state or list of experiment states.
                    E.g. 'Succeeded' or ['Succeeded', 'Preempted']
                    Possible states: 'Creating', 'Waiting', 'Initializing', 'Running',
                        'Cleaning', 'Crashed', 'Failed', 'Aborted', 'Preempted', 'Succeeded'
        :param owner: The owner or list of owners of the experiments. This parameter expects usernames.
        :param tag: A tag or a list of experiment tags. E.g. 'solution-1' or ['solution-1', 'solution-2'].
        :param min_running_time: Minimum running time of an experiment in seconds.
        """
        # TODO: tags - czy teraz jest ok?
        leaderboard_entries = self._fetch_leaderboard(id, group, state, owner, tag, min_running_time)

        def make_row(entry):
            channels = dict(
                ('channel_{}'.format(ch.name), ch.trimmed_y) for ch in entry.channels
            )

            parameters = map_keys(lambda k: 'parameter_{}'.format(k), entry.parameters)
            properties = map_keys(lambda k: 'property_{}'.format(k), entry.properties)

            r = {}
            r.update(entry.system_properties)
            r.update(channels)
            r.update(parameters)
            r.update(properties)
            return r

        rows = ((n, make_row(e)) for (n, e) in enumerate(leaderboard_entries))

        df = pd.DataFrame.from_dict(data=dict(rows), orient='index')
        df = df.reindex(self._sort_leaderboard_columns(df.columns), axis='columns')
        return df

    def get_experiment_groups(self) -> List[str]:
        """
        Retrieve a list of groups in the project.

        :return: A list of group of group IDs, e.g. ['SAN-GRP-1', 'SAN-GRP-2'].
        """
        pass

    @property
    def full_id(self):
        return '{}/{}'.format(self.namespace, self.name)

    def __str__(self):
        return 'Project({})'.format(self.full_id)

    def __repr__(self):
        return str(self)

    def _fetch_leaderboard(self, id, group, state, owner, tag, min_running_time):
        return self.client.get_leaderboard_entries(
            namespace=self.namespace, project_name=self.name,
            ids=as_list(id), group_ids=as_list(group), states=as_list(state),
            owners=as_list(owner), tags=as_list(tag),
            min_running_time=min_running_time)

    @staticmethod
    def _sort_leaderboard_columns(column_names):
        user_defined_weights = {
            'channel': 1,
            'parameter': 2,
            'property': 3
        }

        system_properties_weights = {
            'id': 0,
            'name': 1,
            'created': 2,
            'finished': 3,
            'owner': 4,
            'worker_type': 5,
            'environment': 6,
        }

        def key(c):
            """
            A sorting key for a column name:
                system properties first, then channels, parameters, user-defined properties.

            Within each group columns are sorted alphabetically, except for system properties,
            where order is custom.
            """
            parts = c.split('_', 1)
            if parts[0] in user_defined_weights.keys():
                name = parts[1]
                weight = user_defined_weights.get(parts[0], 99)
                system_property_weight = None
            else:
                name = c
                weight = 0
                system_property_weight = system_properties_weights.get(name, 99)

            return weight, system_property_weight, name

        return sorted(column_names, key=key)
