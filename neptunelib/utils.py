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

from functools import reduce

import numpy as np
import pandas as pd


def map_values(f_value, dictionary):
    return dict(
        (k, f_value(v)) for k, v in dictionary.items()
    )


def map_keys(f_key, dictionary):
    return dict(
        (f_key(k), v) for k, v in dictionary.items()
    )


def as_list(value):
    if value is None or isinstance(value, list):
        return value
    else:
        return [value]


def align_channels_on_x(dataframe):
    x_max = _get_max_x(dataframe)
    joined_x = pd.DataFrame({'x': list(range(x_max + 1))})
    channel_dfs = _split_df_by_stems(dataframe)

    aligned_dfs = []
    for channel_df in channel_dfs:
        aligned_df = pd.merge(joined_x, channel_df, on='x')
        aligned_dfs.append(aligned_df)

    aligned_dfs = merge_dataframes(aligned_dfs, on='x', how='outer')
    return aligned_dfs


def get_channel_name_stems(columns):
    return list(set([col[2:] for col in columns]))


def merge_dataframes(dataframes, on, how='outer'):
    merged_df = reduce(lambda left, right: pd.merge(left, right, on=on, how=how),
                       dataframes)
    return merged_df


def sort_df_by_columns(df):
    df = df.reindex(sorted(df.columns), axis=1)
    return df


def _get_max_x(df):
    x_cols = [col for col in df.columns if col.startswith('x_')]
    x_maxes = [df[col].max() for col in x_cols]
    return int(np.max(x_maxes))


def _split_df_by_stems(df):
    channel_dfs = []
    for stem in get_channel_name_stems(df.columns):
        channel_df = df[['x_{}'.format(stem), 'y_{}'.format(stem)]]
        channel_df.columns = ['x', stem]
        channel_dfs.append(channel_df)
    return channel_dfs
