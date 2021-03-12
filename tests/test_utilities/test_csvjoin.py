#!/usr/bin/env python

import sys

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkit.utilities.csvjoin import CSVJoin, launch_new_instance
from tests.utils import CSVKitTestCase, EmptyFileTests


class TestCSVJoin(CSVKitTestCase, EmptyFileTests):
    Utility = CSVJoin
    default_args = ['examples/dummy.csv', '-']

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/join_a.csv', 'examples/join_b.csv']):
            launch_new_instance()

    def test_sequential(self):
        output = self.get_output_as_io(['examples/join_a.csv', 'examples/join_b.csv'])
        self.assertEqual(len(output.readlines()), 4)

    def test_inner(self):
        output = self.get_output_as_io(['-c', 'a', 'examples/join_a.csv', 'examples/join_b.csv'])
        self.assertEqual(len(output.readlines()), 3)

    def test_left(self):
        output = self.get_output_as_io(['-c', 'a', '--left', 'examples/join_a.csv', 'examples/join_b.csv'])
        self.assertEqual(len(output.readlines()), 5)

    def test_right(self):
        output = self.get_output_as_io(['-c', 'a', '--right', 'examples/join_a.csv', 'examples/join_b.csv'])
        self.assertEqual(len(output.readlines()), 4)

    def test_outer(self):
        output = self.get_output_as_io(['-c', 'a', '--outer', 'examples/join_a.csv', 'examples/join_b.csv'])
        self.assertEqual(len(output.readlines()), 6)

    def test_left_short_columns(self):
        output = self.get_output_as_io(['-c', 'a', 'examples/join_a_short.csv', 'examples/join_b.csv'])
        with open('examples/join_short.csv') as f:
            self.assertEqual(output.readlines(), f.readlines())

    def test_single(self):
        self.assertRows(['examples/dummy.csv', '--no-inference'], [
            ['a', 'b', 'c'],
            ['1', '2', '3'],
        ])

    def test_no_blanks(self):
        self.assertRows(['examples/blanks.csv', 'examples/blanks.csv'], [
            ['a', 'b', 'c', 'd', 'e', 'f', 'a2', 'b2', 'c2', 'd2', 'e2', 'f2'],
            ['', '', '', '', '', '', '', '', '', '', '', ''],
        ])

    def test_blanks(self):
        self.assertRows(['--blanks', 'examples/blanks.csv', 'examples/blanks.csv'], [
            ['a', 'b', 'c', 'd', 'e', 'f', 'a2', 'b2', 'c2', 'd2', 'e2', 'f2'],
            ['', 'NA', 'N/A', 'NONE', 'NULL', '.', '', 'NA', 'N/A', 'NONE', 'NULL', '.'],
        ])

    def test_no_header_row(self):
        output = self.get_output_as_io(['-c', '1', '--no-header-row', 'examples/join_a.csv', 'examples/join_no_header_row.csv'])
        self.assertEqual(len(output.readlines()), 3)

    def test_no_inference(self):
        self.assertRows(['--no-inference', 'examples/join_a.csv', 'examples/join_short.csv'], [
            ['a', 'b', 'c', 'a2', 'b2', 'c2', 'b2_2', 'c2_2'],
            ['1', 'b', 'c', '1', 'b', '', 'b', 'c'],
            ['2', 'b', 'c', '1', 'b', '', 'b', 'c'],
            ['3', 'b', 'c', '', '', '', '', ''],
        ])

    def test_sniff_limit_default(self):
        self.assertRows(['examples/join_a.csv', 'examples/sniff_limit.csv'], [
            ['a', 'b', 'c', 'a2', 'b2', 'c2'],
            ['1', 'b', 'c', 'True', '2', '3'],
            ['2', 'b', 'c', '', '', ''],
            ['3', 'b', 'c', '', '', ''],
        ])

    def test_sniff_limit_zero_limit(self):
        self.assertRows(['--snifflimit', '0', 'examples/join_a.csv', 'examples/sniff_limit.csv'], [
            ['a', 'b', 'c', 'a;b;c'],
            ['1', 'b', 'c', '1;2;3'],
            ['2', 'b', 'c', ''],
            ['3', 'b', 'c', ''],
        ])
