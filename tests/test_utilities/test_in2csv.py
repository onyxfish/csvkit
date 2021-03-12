#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import six

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkit.utilities.in2csv import In2CSV, launch_new_instance
from tests.utils import CSVKitTestCase, EmptyFileTests, stdin_as_string


class TestIn2CSV(CSVKitTestCase, EmptyFileTests):
    Utility = In2CSV
    default_args = ['-f', 'csv']

    def assertConverted(self, input_format, input_filename, output_filename, additional_args=[]):
        output = self.get_output(['-f', input_format, input_filename] + additional_args)

        with open(output_filename, 'r') as f:
            self.assertEqual(output, f.read())

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/dummy.csv']):
            launch_new_instance()

    def test_version(self):
        with self.assertRaises(SystemExit) as e:
            self.get_output(['-V'])

        self.assertEqual(e.exception.code, 0)

    def test_locale(self):
        self.assertConverted('csv', 'examples/test_locale.csv', 'examples/test_locale_converted.csv', ['--locale', 'de_DE'])

    def test_no_blanks(self):
        self.assertConverted('csv', 'examples/blanks.csv', 'examples/blanks_converted.csv')

    def test_blanks(self):
        self.assertConverted('csv', 'examples/blanks.csv', 'examples/blanks.csv', ['--blanks'])

    def test_date_format(self):
        self.assertConverted('csv', 'examples/test_date_format.csv', 'examples/test_date_format_converted.csv', ['--date-format', '%d/%m/%Y'])

    def test_date_format_default(self):
        self.assertConverted('csv', 'examples/test_date_format.csv', 'examples/test_date_format.csv')

    def test_numeric_date_format(self):
        self.assertConverted('csv', 'examples/test_numeric_date_format.csv', 'examples/test_date_format_converted.csv', ['--date-format', '%Y%m%d'])

    def test_numeric_date_format_default(self):
        self.assertConverted('csv', 'examples/test_numeric_date_format.csv', 'examples/test_numeric_date_format.csv')

    def test_date_like_number(self):
        self.assertConverted('csv', 'examples/date_like_number.csv', 'examples/date_like_number.csv')

    def test_convert_csv(self):
        self.assertConverted('csv', 'examples/testfixed_converted.csv', 'examples/testfixed_converted.csv')

    def test_convert_csv_with_skip_lines(self):
        self.assertConverted('csv', 'examples/test_skip_lines.csv', 'examples/dummy.csv', ['--skip-lines', '3', '--no-inference'])

    def test_convert_tsv(self):
        self.assertConverted('csv', 'examples/dummy.tsv', 'examples/dummy.csv', ['--no-inference'])

    def test_convert_tsv_streaming(self):
        self.assertConverted('csv', 'examples/dummy.tsv', 'examples/dummy.csv', ['--no-inference', '--snifflimit', '0', '--tabs'])

    def test_convert_dbf(self):
        self.assertConverted('dbf', 'examples/testdbf.dbf', 'examples/testdbf_converted.csv')

    def test_convert_json(self):
        self.assertConverted('json', 'examples/testjson.json', 'examples/testjson_converted.csv')

    def test_convert_geojson(self):
        self.assertConverted('geojson', 'examples/test_geojson.json', 'examples/test_geojson.csv')

    def test_convert_ndjson(self):
        self.assertConverted('ndjson', 'examples/testjson_multiline.json', 'examples/testjson_multiline_converted.csv')

    def test_convert_nested_json(self):
        self.assertConverted('json', 'examples/testjson_nested.json', 'examples/testjson_nested_converted.csv')

    def test_convert_xls(self):
        self.assertConverted('xls', 'examples/test.xls', 'examples/testxls_converted.csv')

    def test_convert_xls_with_sheet(self):
        self.assertConverted('xls', 'examples/sheets.xls', 'examples/testxls_converted.csv', ['--sheet', 'data'])

    def test_convert_xls_with_unicode_sheet(self):
        self.assertLines(['--sheet', 'ʤ', 'examples/sheets.xls'], [
            'a,b,c',
            '1.0,2.0,3.0',
        ])

    def test_convert_xls_with_skip_lines(self):
        self.assertConverted('xls', 'examples/test_skip_lines.xls', 'examples/testxls_converted.csv', ['--skip-lines', '3'])

    def test_convert_xlsx(self):
        self.assertConverted('xlsx', 'examples/test.xlsx', 'examples/testxlsx_converted.csv')

    def test_convert_xlsx_with_sheet(self):
        self.assertConverted('xlsx', 'examples/sheets.xlsx', 'examples/testxlsx_converted.csv', ['--sheet', 'data'])

    def test_convert_xlsx_with_unicode_sheet(self):
        self.assertLines(['--sheet', 'ʤ', '--no-inference', 'examples/sheets.xlsx'], [
            'a,b,c',
            '1,2,3',
        ])

    def test_convert_xlsx_with_skip_lines(self):
        self.assertConverted('xlsx', 'examples/test_skip_lines.xlsx', 'examples/testxlsx_converted.csv', ['--skip-lines', '3'])

    def test_names(self):
        self.assertLines(['--names', 'examples/sheets.xlsx'], [
            'not this one',
            'data',
            u'ʤ',
        ])

    def test_csv_no_headers(self):
        self.assertConverted('csv', 'examples/no_header_row.csv', 'examples/dummy.csv', ['--no-header-row', '--no-inference'])

    def test_csv_no_headers_streaming(self):
        self.assertConverted('csv', 'examples/no_header_row.csv', 'examples/dummy.csv', ['--no-header-row', '--no-inference', '--snifflimit', '0'])

    def test_csv_datetime_inference(self):
        input_file = six.StringIO('a\n2015-01-01T00:00:00Z')

        with stdin_as_string(input_file):
            self.assertLines(['-f', 'csv'], [
                'a',
                '2015-01-01T00:00:00+00:00',
            ])

        input_file.close()

    def test_csv_no_inference(self):
        self.assertLines(['--no-inference', 'examples/dummy.csv'], [
            'a,b,c',
            '1,2,3',
        ])

    def test_xls_no_inference(self):
        self.assertLines(['--no-inference', 'examples/dummy.xls'], [
            'a,b,c',
            '1.0,2.0,3.0',
        ])

    def test_xlsx_no_inference(self):
        self.assertLines(['--no-inference', 'examples/dummy.xlsx'], [
            'a,b,c',
            '1,2,3',
        ])

    def test_geojson_no_inference(self):
        input_file = six.StringIO('{"a": 1, "b": 2, "type": "FeatureCollection", "features": [{"geometry": {}, "properties": {"a": 1, "b": 2, "c": 3}}]}')

        with stdin_as_string(input_file):
            self.assertLines(['--no-inference', '-f', 'geojson'], [
                'id,a,b,c,geojson,type,longitude,latitude',
                ',1,2,3,{},,,',
            ])

        input_file.close()

    def test_json_no_inference(self):
        input_file = six.StringIO('[{"a": 1, "b": 2, "c": 3}]')

        with stdin_as_string(input_file):
            self.assertLines(['--no-inference', '-f', 'json'], [
                'a,b,c',
                '1,2,3',
            ])

        input_file.close()

    def test_ndjson_no_inference(self):
        input_file = six.StringIO('{"a": 1, "b": 2, "c": 3}')

        with stdin_as_string(input_file):
            self.assertLines(['--no-inference', '-f', 'ndjson'], [
                'a,b,c',
                '1,2,3',
            ])

        input_file.close()

    def test_names_xls(self):
        output = self.get_output_as_io(['-n', 'examples/sheets.xls'])

        self.assertEqual(next(output), 'not this one\n')
        self.assertEqual(next(output), 'data\n')

    def test_names_xlsx(self):
        output = self.get_output_as_io(['-n', 'examples/sheets.xlsx'])

        self.assertEqual(next(output), 'not this one\n')
        self.assertEqual(next(output), 'data\n')

    def test_convert_xls_with_write_sheets(self):
        try:
            self.assertConverted('xls', 'examples/sheets.xls', 'examples/testxls_converted.csv', ['--sheet', 'data', '--write-sheets', "ʤ,1"])
            with open('examples/sheets_0.csv', 'r') as f:
                with open('examples/testxls_unicode_converted.csv', 'r') as g:
                    self.assertEqual(f.read(), g.read())
            with open('examples/sheets_1.csv', 'r') as f:
                with open('examples/testxls_converted.csv', 'r') as g:
                    self.assertEqual(f.read(), g.read())
            self.assertFalse(os.path.exists('examples/sheets_2.csv'))
        finally:
            for suffix in (0, 1):
                path = 'examples/sheets_%d.csv' % suffix
                if os.path.exists(path):
                    os.remove(path)

    def test_convert_xlsx_with_write_sheets(self):
        try:
            self.assertConverted('xlsx', 'examples/sheets.xlsx', 'examples/testxlsx_noinference_converted.csv', ['--no-inference', '--sheet', 'data', '--write-sheets', "ʤ,1"])
            with open('examples/sheets_0.csv', 'r') as f:
                with open('examples/testxlsx_unicode_converted.csv', 'r') as g:
                    self.assertEqual(f.read(), g.read())
            with open('examples/sheets_1.csv', 'r') as f:
                with open('examples/testxlsx_noinference_converted.csv', 'r') as g:
                    self.assertEqual(f.read(), g.read())
            self.assertFalse(os.path.exists('examples/sheets_2.csv'))
        finally:
            for suffix in (0, 1):
                path = 'examples/sheets_%d.csv' % suffix
                if os.path.exists(path):
                    os.remove(path)

    def test_convert_xls_with_write_sheets_with_names(self):
        try:
            self.assertConverted('xls', 'examples/sheets.xls', 'examples/testxls_converted.csv', ['--sheet', 'data', '--write-sheets', "ʤ,1", '--write-sheet-names'])
            with open('examples/sheets_ʤ.csv', 'r') as f:
                with open('examples/testxls_unicode_converted.csv', 'r') as g:
                    self.assertEqual(f.read(), g.read())
            with open('examples/sheets_data.csv', 'r') as f:
                with open('examples/testxls_converted.csv', 'r') as g:
                    self.assertEqual(f.read(), g.read())
            self.assertFalse(os.path.exists('examples/sheets_0.csv'))
            self.assertFalse(os.path.exists('examples/sheets_1.csv'))
            self.assertFalse(os.path.exists('examples/sheets_2.csv'))
        finally:
            for suffix in ('ʤ', 'data'):
                path = 'examples/sheets_%s.csv' % suffix
                if os.path.exists(path):
                    os.remove(path)

    def test_convert_xlsx_with_write_sheets_with_names(self):
        try:
            self.assertConverted('xlsx', 'examples/sheets.xlsx', 'examples/testxlsx_noinference_converted.csv', ['--no-inference', '--sheet', 'data', '--write-sheets', "ʤ,1", '--write-sheet-names'])
            with open('examples/sheets_ʤ.csv', 'r') as f:
                with open('examples/testxlsx_unicode_converted.csv', 'r') as g:
                    self.assertEqual(f.read(), g.read())
            with open('examples/sheets_data.csv', 'r') as f:
                with open('examples/testxlsx_noinference_converted.csv', 'r') as g:
                    self.assertEqual(f.read(), g.read())
            self.assertFalse(os.path.exists('examples/sheets_0.csv'))
            self.assertFalse(os.path.exists('examples/sheets_1.csv'))
            self.assertFalse(os.path.exists('examples/sheets_2.csv'))
        finally:
            for suffix in ('ʤ', 'data'):
                path = 'examples/sheets_%s.csv' % suffix
                if os.path.exists(path):
                    os.remove(path)

    def test_convert_xlsx_with_write_sheets_with_names_and_regexp(self):
        try:
            self.assertConverted('xlsx', 'examples/sheets.xlsx', 'examples/testxlsx_noinference_converted.csv', ['--no-inference', '-r', '--write-sheets', "[a-z]+", '--write-sheet-names'])
            with open('examples/sheets_data.csv', 'r') as f:
                with open('examples/testxlsx_noinference_converted.csv', 'r') as g:
                    self.assertEqual(f.read(), g.read())
            self.assertFalse(os.path.exists('examples/sheets_0.csv'))
            self.assertFalse(os.path.exists('examples/sheets_1.csv'))
            self.assertFalse(os.path.exists('examples/sheets_2.csv'))
        finally:
            for suffix in ('data',):
                path = 'examples/sheets_%s.csv' % suffix
                if os.path.exists(path):
                    os.remove(path)
