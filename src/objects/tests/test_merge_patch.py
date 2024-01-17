from unittest import TestCase

from objects.api.utils import merge_patch


class MergePatchTests(TestCase):
    def test_merge_patch(self):
        test_data = [
            ({"a": "b"}, {"a": "c"}, {"a": "c"}),
            ({"a": "b"}, {"b": "c"}, {"a": "b", "b": "c"}),
            ({"a": "b"}, {"a": None}, {"a": None}),
            ({"a": "b", "b": "c"}, {"a": None}, {"a": None, "b": "c"}),
            ({"a": ["b"]}, {"a": "c"}, {"a": "c"}),
            ({"a": "c"}, {"a": ["b"]}, {"a": ["b"]}),
            (
                {"a": {"b": "c"}},
                {"a": {"b": "d", "c": None}},
                {"a": {"b": "d", "c": None}},
            ),
            ({"a": [{"b": "c"}]}, {"a": [1]}, {"a": [1]}),
            (["a", "b"], ["c", "d"], ["c", "d"]),
            ({"a": "b"}, ["c"], ["c"]),
            ({"a": "foo"}, None, None),
            ({"a": "foo"}, "bar", "bar"),
            ({"e": None}, {"a": 1}, {"e": None, "a": 1}),
            ([1, 2], {"a": "b", "c": None}, {"a": "b", "c": None}),
            ({}, {"a": {"bb": {"ccc": None}}}, {"a": {"bb": {"ccc": None}}}),
            ({"a": "b"}, {"a": "b"}, {"a": "b"}),
        ]

        for target, patch, expected in test_data:
            with self.subTest():
                self.assertEqual(merge_patch(target, patch), expected)
