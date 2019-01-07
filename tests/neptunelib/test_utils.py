import unittest

from neptunelib.utils import map_keys, map_values, as_list


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


def times_2(x):
    return x * 2


if __name__ == '__main__':
    unittest.main()
