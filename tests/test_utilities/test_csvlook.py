#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import six

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkit.utilities.csvlook import CSVLook, launch_new_instance
from tests.utils import CSVKitTestCase, EmptyFileTests, stdin_as_string


class TestCSVLook(CSVKitTestCase, EmptyFileTests):
    Utility = CSVLook

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/dummy.csv']):
            launch_new_instance()

    def test_runs(self):
        if sys.version_info < (3,):
            self.get_output(['examples/test_utf8.csv'])
        else:
            self.assertLines(['examples/test_utf8.csv'], [
                '| foo | bar | baz |',
                '| --- | --- | --- |',
                '|   1 |   2 | 3   |',
                '|   4 |   5 | ʤ   |',
            ])

    def test_encoding(self):
        if sys.version_info < (3,):
            self.get_output(['-e', 'latin1', 'examples/test_latin1.csv'])
        else:
            self.assertLines(['-e', 'latin1', 'examples/test_latin1.csv'], [
                '| a | b | c |',
                '| - | - | - |',
                '| 1 | 2 | 3 |',
                '| 4 | 5 | © |',
            ])

    def test_simple(self):
        self.assertLines(['examples/dummy3.csv'], [
            '|    a | b | c |',
            '| ---- | - | - |',
            '| True | 2 | 3 |',
            '| True | 4 | 5 |',
        ])

    def test_no_blanks(self):
        self.assertLines(['examples/blanks.csv'], [
            '| a | b | c | d | e | f |',
            '| - | - | - | - | - | - |',
            '|   |   |   |   |   |   |',
        ])

    def test_blanks(self):
        self.assertLines(['--blanks', 'examples/blanks.csv'], [
            '| a | b  | c   | d    | e    | f |',
            '| - | -- | --- | ---- | ---- | - |',
            '|   | NA | N/A | NONE | NULL | . |',
        ])

    def test_no_header_row(self):
        self.assertLines(['--no-header-row', 'examples/no_header_row3.csv'], [
            '| a | b | c |',
            '| - | - | - |',
            '| 1 | 2 | 3 |',
            '| 4 | 5 | 6 |',
        ])

    def test_unicode(self):
        self.assertLines(['examples/test_utf8.csv'], [
            '| foo | bar | baz |',
            '| --- | --- | --- |',
            '|   1 |   2 | 3   |',
            u'|   4 |   5 | ʤ   |',
        ])

    def test_unicode_bom(self):
        self.assertLines(['examples/test_utf8_bom.csv'], [
            '| foo | bar | baz |',
            '| --- | --- | --- |',
            '|   1 |   2 | 3   |',
            u'|   4 |   5 | ʤ   |',
        ])

    def test_linenumbers(self):
        self.assertLines(['--linenumbers', 'examples/dummy3.csv'], [
            '| line_numbers |    a | b | c |',
            '| ------------ | ---- | - | - |',
            '|            1 | True | 2 | 3 |',
            '|            2 | True | 4 | 5 |',
        ])

    def test_no_inference(self):
        self.assertLines(['--no-inference', 'examples/dummy3.csv'], [
            '| a | b | c |',
            '| - | - | - |',
            '| 1 | 2 | 3 |',
            '| 1 | 4 | 5 |',
        ])

    def test_sniff_limit_default(self):
        self.assertLines(['examples/sniff_limit.csv'], [
            '|    a | b | c |',
            '| ---- | - | - |',
            '| True | 2 | 3 |',
        ])

    def test_sniff_limit_zero_limit(self):
        self.assertLines(['--snifflimit', '0', 'examples/sniff_limit.csv'], [
            '| a;b;c |',
            '| ----- |',
            '| 1;2;3 |',
        ])

    def test_max_rows(self):
        self.assertLines(['--max-rows', '0', 'examples/dummy.csv'], [
            '| a | b | c |',
            '| - | - | - |',
            '| ... | ... | ... |',
        ])

    def test_max_columns(self):
        self.assertLines(['--max-columns', '1', 'examples/dummy.csv'], [
            '|    a | ... |',
            '| ---- | --- |',
            '| True | ... |',
        ])

    def test_max_column_width(self):
        self.assertLines(['--max-column-width', '1', 'examples/dummy.csv'], [
            '|     a | b | c |',
            '| ----- | - | - |',
            '| Tr... | 2 | 3 |',
        ])

    def test_stdin(self):
        input_file = six.StringIO('a,b,c\n1,2,3\n4,5,6\n')

        with stdin_as_string(input_file):
            self.assertLines([], [
                '| a | b | c |',
                '| - | - | - |',
                '| 1 | 2 | 3 |',
                '| 4 | 5 | 6 |',
            ])

        input_file.close()
