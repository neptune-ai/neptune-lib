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

import unittest

import numpy as np
import pandas as pd
from pandas.util.testing import assert_frame_equal

from neptunelib.utils import map_keys, map_values, as_list, align_channels_on_x, get_channel_name_stems, \
    merge_dataframes, sort_df_by_columns


class TestMapValues(unittest.TestCase):
    def test_empty_map(self):
        # when
        mapped_dict = map_values(times_2, {})

        # then
        self.assertEqual({}, mapped_dict)

    def test_non_empty_map(self):
        # when
        mapped_dict = map_values(times_2, {'a': 2, 'b': 3})

        # then
        self.assertEqual({'a': 4, 'b': 6}, mapped_dict)


class TestMapKeys(unittest.TestCase):
    def test_empty_map(self):
        # when
        mapped_dict = map_keys(times_2, {})

        # then
        self.assertEqual({}, mapped_dict)

    def test_non_empty_map(self):
        # when
        mapped_dict = map_keys(times_2, {2: 'a', 3: 'b'})

        # then
        self.assertEqual({4: 'a', 6: 'b'}, mapped_dict)


class TestAsList(unittest.TestCase):

    def test_none(self):
        # expect
        self.assertEqual(None, as_list(None))

    def test_scalar(self):
        # expect
        self.assertEqual([1], as_list(1))

    def test_list(self):
        # expect
        self.assertEqual([2], as_list([2]))

    def test_dict(self):
        self.assertEqual([{'a': 1}], as_list({'a': 1}))


class TestAlignChannelsOnX(unittest.TestCase):

    def setUp(self):
        np.random.seed(1234)
        random_batch = np.random.random(10).tolist()
        random_epoch = np.random.random(5).tolist()
        random_odd = np.random.random(7).tolist()

        self.df = pd.DataFrame({'x_batch_channel': list(range(10)),
                                'y_batch_channel': random_batch,
                                'x_epoch_channel': list(range(5)) + [np.nan] * 5,
                                'y_epoch_channel': random_epoch + [np.nan] * 5,
                                'x_odd_channel': list(range(7)) + [np.nan] * 3,
                                'y_odd_channel': random_odd + [np.nan] * 3})

        aligned_df = pd.DataFrame({'x': list(range(10)),
                                   'batch_channel': random_batch,
                                   'epoch_channel': random_epoch + [np.nan] * 5,
                                   'odd_channel': random_odd + [np.nan] * 3})

        self.aligned_df = sort_df_by_columns(aligned_df)

    def test_aligned(self):
        result = align_channels_on_x(self.df)
        result = sort_df_by_columns(result)

        assert_frame_equal(result, self.aligned_df)


class TestGetChannelNameStems(unittest.TestCase):

    def setUp(self):
        np.random.seed(1234)
        self.df = pd.DataFrame({'x_batch_channel': list(range(10)),
                                'y_batch_channel': np.random.random(10),
                                'x_epoch_channel': list(range(5)) + [np.nan] * 5,
                                'y_epoch_channel': np.random.random(10),
                                'x_odd_channel': list(range(7)) + [np.nan] * 3,
                                'y_odd_channel': np.random.random(10)})

    def test_names(self):
        correct_names = set(['epoch_channel', 'batch_channel', 'odd_channel'])
        self.assertEqual(set(get_channel_name_stems(self.df)), correct_names)


class TestMergeDataFrames(unittest.TestCase):

    def setUp(self):
        np.random.seed(1234)
        random_df1 = np.random.random(10).tolist()
        self.df1 = pd.DataFrame({'x': list(range(10)),
                                 'y1': random_df1})

        random_df2 = np.random.random(3).tolist()
        self.df2 = pd.DataFrame({'x': list(range(3)),
                                 'y2': random_df2})

        random_df3 = np.random.random(6).tolist()
        self.df3 = pd.DataFrame({'x': list(range(6)),
                                 'y3': random_df3})

        df_merged_outer = pd.DataFrame({'x': list(range(10)),
                                        'y1': random_df1,
                                        'y2': random_df2 + [np.nan] * 7,
                                        'y3': random_df3 + [np.nan] * 4})

        self.df_merged_outer = sort_df_by_columns(df_merged_outer)

    def test_merge_outer(self):
        result = merge_dataframes([self.df1, self.df2, self.df3], on='x', how='outer')
        result = sort_df_by_columns(result)
        assert_frame_equal(result, self.df_merged_outer)


class TestSortDfByColumns(unittest.TestCase):

    def test_letters_and_numbers(self):
        sorted_df = pd.DataFrame(columns=['1', '2', '3', 'a', 'b', 'c', 'd', ])
        shuffled_df = pd.DataFrame(columns=['c', 'a', '1', 'd', '3', '2', 'b'])

        assert_frame_equal(sort_df_by_columns(shuffled_df), sorted_df)


def times_2(x):
    return x * 2


if __name__ == '__main__':
    unittest.main()
