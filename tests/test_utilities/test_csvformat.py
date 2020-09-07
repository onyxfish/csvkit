#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import six

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkit.utilities.csvformat import CSVFormat, launch_new_instance
from tests.utils import CSVKitTestCase, EmptyFileTests, stdin_as_string


class TestCSVFormat(CSVKitTestCase, EmptyFileTests):
    Utility = CSVFormat

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/dummy.csv']):
            launch_new_instance()

    def test_skip_lines(self):
        self.assertLines(['--skip-lines', '3', '-D', '|', 'examples/test_skip_lines.csv'], [
            'a|b|c',
            '1|2|3',
        ])

    def test_no_header_row(self):
        self.assertLines(['--no-header-row', 'examples/no_header_row.csv'], [
            '1,2,3',
        ])

    def test_linenumbers(self):
        self.assertLines(['--linenumbers', 'examples/dummy.csv'], [
            'line_number,a,b,c',
            '1,1,2,3',
        ])

    def test_delimiter(self):
        self.assertLines(['-D', '|', 'examples/dummy.csv'], [
            'a|b|c',
            '1|2|3',
        ])

    def test_tab_delimiter(self):
        self.assertLines(['-T', 'examples/dummy.csv'], [
            'a\tb\tc',
            '1\t2\t3',
        ])

    def test_quotechar(self):
        input_file = six.StringIO('a,b,c\n1*2,3,4\n')

        with stdin_as_string(input_file):
            self.assertLines(['-Q', '*'], [
                'a,b,c',
                '*1**2*,3,4',
            ])

        input_file.close()

    def test_doublequote(self):
        input_file = six.StringIO('a\n"a ""quoted"" string"')

        with stdin_as_string(input_file):
            self.assertLines(['-P', '#', '-B'], [
                'a',
                'a #"quoted#" string',
            ])

        input_file.close()

    def test_escapechar(self):
        input_file = six.StringIO('a,b,c\n1"2,3,4\n')

        with stdin_as_string(input_file):
            self.assertLines(['-P', '#', '-U', '3'], [
                'a,b,c',
                '1#"2,3,4',
            ])

        input_file.close()

    def test_out_quoting(self):
        input_file = six.StringIO('4,b,6,d,e\na,2,3,d,NA\n8,9,,z,10\n1.1,2.0,3.00,,11\n')

        with stdin_as_string(input_file):
            self.assertLines(['-U', '2'], [
                '"4","b","6","d","e"',
                '"a",2,3,"d","NA"',
                '"8",9,"","z","10"',
                '"1.1",2.0,3.00,"","11"',
            ])

        input_file.close()

    def test_out_quoting_no_header_row(self):
        input_file = six.StringIO('4,5,6,7\na,2,3,d\n8,9,,z\n')

        with stdin_as_string(input_file):
            self.assertLines(['-U', '2', '--no-header-row'], [
                '"4",5,6,"7"',
                '"a",2,3,"d"',
                '"8",9,"","z"',
            ])

        input_file.close()

    def test_lineterminator(self):
        self.assertLines(['-M', 'XYZ', 'examples/dummy.csv'], [
            'a,b,cXYZ1,2,3XYZ',
        ], newline_at_eof=False)
