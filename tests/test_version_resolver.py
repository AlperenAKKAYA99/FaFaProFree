#!/usr/bin/env python3
"""
Unit tests for FaFaProFree version resolver & semver sorting.
"""

import unittest
from scripts.version_resolver import (
    clean_version_str,
    parse_semver,
    sort_versions_descending,
    group_versions_by_major
)


class TestVersionResolver(unittest.TestCase):

    def test_clean_version_str(self):
        self.assertEqual(clean_version_str("v7.3.1"), "7.3.1")
        self.assertEqual(clean_version_str("Release 7.3.0"), "7.3.0")
        self.assertEqual(clean_version_str("  v6.7.2  "), "6.7.2")

    def test_parse_semver(self):
        self.assertEqual(parse_semver("7.3.1"), (7, 3, 1, ""))
        self.assertEqual(parse_semver("6.5.2-beta.1"), (6, 5, 2, "beta.1"))
        self.assertEqual(parse_semver("5.15.4"), (5, 15, 4, ""))

    def test_sort_versions_descending(self):
        versions = ["6.7.2", "7.3.0", "5.15.4", "7.3.1", "7.2.0"]
        sorted_v = sort_versions_descending(versions)
        self.assertEqual(sorted_v, ["7.3.1", "7.3.0", "7.2.0", "6.7.2", "5.15.4"])

    def test_group_versions_by_major(self):
        versions = ["7.3.1", "7.3.0", "6.7.2", "5.15.4"]
        grouped = group_versions_by_major(versions)
        self.assertIn("v7", grouped)
        self.assertIn("v6", grouped)
        self.assertIn("v5", grouped)
        self.assertEqual(len(grouped["v7"]), 2)
        self.assertEqual(len(grouped["v6"]), 1)
        self.assertEqual(len(grouped["v5"]), 1)


if __name__ == "__main__":
    unittest.main()
