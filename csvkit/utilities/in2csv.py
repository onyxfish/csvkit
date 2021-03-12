#!/usr/bin/env python
import re
import sys
from os.path import splitext

import agate
import agatedbf  # noqa
import agateexcel  # noqa
import openpyxl
import six
import xlrd

from csvkit import convert
from csvkit.convert.fixed import fixed2csv
from csvkit.convert.geojs import geojson2csv
from csvkit.cli import CSVKitUtility

SUPPORTED_FORMATS = ['csv', 'dbf', 'fixed', 'geojson', 'json', 'ndjson', 'xls', 'xlsx']


class In2CSV(CSVKitUtility):
    description = 'Convert common, but less awesome, tabular data formats to CSV.'
    epilog = 'Some command-line flags only pertain to specific input formats.'
    # The utility handles the input file.
    override_flags = ['f']

    def add_arguments(self):
        # I feel that there ought to be a better way to do this across Python 2 and 3.
        def option_parser(bytestring):
            if six.PY2:
                return bytestring.decode(sys.getfilesystemencoding())
            else:
                return bytestring

        self.argparser.add_argument(metavar='FILE', nargs='?', dest='input_path',
                                    help='The CSV file to operate on. If omitted, will accept input as piped data via STDIN.')
        self.argparser.add_argument('-f', '--format', dest='filetype',
                                    help='The format of the input file. If not specified will be inferred from the file type. Supported formats: %s.' % ', '.join(sorted(SUPPORTED_FORMATS)))
        self.argparser.add_argument('-s', '--schema', dest='schema',
                                    help='Specify a CSV-formatted schema file for converting fixed-width files.  See documentation for details.')
        self.argparser.add_argument('-k', '--key', dest='key',
                                    help='Specify a top-level key to use look within for a list of objects to be converted when processing JSON.')
        self.argparser.add_argument('-n', '--names', dest='names_only', action='store_true',
                                    help='Display sheet names from the input Excel file.')
        self.argparser.add_argument('--sheet', dest='sheet', type=option_parser,
                                    help='The name of the Excel sheet to operate on.')
        self.argparser.add_argument('--write-sheets', dest='write_sheets', type=option_parser,
                                    help='The names of the Excel sheets to write to files, or "-" to write all sheets.')
        self.argparser.add_argument('--write-sheet-names', dest='write_sheet_names', action='store_true',
                                    help='Use the sheet name to create the target filename when using --write-sheets.')
        self.argparser.add_argument('-r', '--regular-expression', dest='regular_expression', action='store_true',
                                    help='Use regular expression to identify XLS sheet names when using --write-sheets.')
        self.argparser.add_argument('--encoding-xls', dest='encoding_xls',
                                    help='Specify the encoding of the input XLS file.')
        self.argparser.add_argument('-y', '--snifflimit', dest='sniff_limit', type=int,
                                    help='Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely.')
        self.argparser.add_argument('-I', '--no-inference', dest='no_inference', action='store_true',
                                    help='Disable type inference (and --locale, --date-format, --datetime-format) when parsing CSV input.')

    def open_excel_input_file(self, path):
        if not path or path == '-':
            if six.PY2:
                return six.BytesIO(sys.stdin.read())
            else:
                return six.BytesIO(sys.stdin.buffer.read())
        else:
            return open(path, 'rb')

    def sheet_names(self, path, filetype):
        input_file = self.open_excel_input_file(path)
        if filetype == 'xls':
            sheet_names = xlrd.open_workbook(file_contents=input_file.read()).sheet_names()
        else:  # 'xlsx'
            sheet_names = openpyxl.load_workbook(input_file, read_only=True, data_only=True).sheetnames
        input_file.close()
        return sheet_names

    def main(self):
        path = self.args.input_path

        # Determine the file type.
        if self.args.filetype:
            filetype = self.args.filetype
            if filetype not in SUPPORTED_FORMATS:
                self.argparser.error('"%s" is not a supported format' % self.args.filetype)
        elif self.args.schema:
            filetype = 'fixed'
        elif self.args.key:
            filetype = 'json'
        else:
            if not path or path == '-':
                self.argparser.error('You must specify a format when providing input as piped data via STDIN.')
            filetype = convert.guess_format(path)
            if not filetype:
                self.argparser.error('Unable to automatically determine the format of the input file. Try specifying a format with --format.')

        if self.args.names_only:
            if filetype in ('xls', 'xlsx'):
                sheets = self.sheet_names(path, filetype)
                for sheet in sheets:
                    self.output_file.write('%s\n' % sheet)
            else:
                self.argparser.error('You cannot use the -n or --names options with non-Excel files.')
            return

        # Set the input file.
        if filetype in ('xls', 'xlsx'):
            self.input_file = self.open_excel_input_file(path)
        else:
            self.input_file = self._open_input_file(path)

        # Set the reader's arguments.
        kwargs = {}

        if self.args.schema:
            schema = self._open_input_file(self.args.schema)
        elif filetype == 'fixed':
            raise ValueError('schema must not be null when format is "fixed"')

        if filetype == 'csv':
            kwargs.update(self.reader_kwargs)
            kwargs['sniff_limit'] = self.args.sniff_limit

        if filetype in ('xls', 'xlsx'):
            kwargs['header'] = not self.args.no_header_row

        if filetype not in ('dbf', 'geojson', 'json', 'ndjson'):  # csv, fixed, xls, xlsx
            kwargs['skip_lines'] = self.args.skip_lines

        if filetype != 'dbf':
            kwargs['column_types'] = self.get_column_types()

        # Convert the file.
        if filetype == 'csv' and self.args.no_inference and not self.args.no_header_row and not self.args.skip_lines and self.args.sniff_limit == 0:
            reader = agate.csv.reader(self.input_file, **self.reader_kwargs)
            writer = agate.csv.writer(self.output_file, **self.writer_kwargs)
            writer.writerows(reader)
        elif filetype == 'fixed':
            self.output_file.write(fixed2csv(self.input_file, schema, output=self.output_file, **kwargs))
        elif filetype == 'geojson':
            self.output_file.write(geojson2csv(self.input_file, **kwargs))
        elif filetype in ('csv', 'dbf', 'json', 'ndjson', 'xls', 'xlsx'):
            if filetype == 'csv':
                table = agate.Table.from_csv(self.input_file, **kwargs)
            elif filetype == 'json':
                table = agate.Table.from_json(self.input_file, key=self.args.key, **kwargs)
            elif filetype == 'ndjson':
                table = agate.Table.from_json(self.input_file, key=self.args.key, newline=True, **kwargs)
            elif filetype == 'xls':
                table = agate.Table.from_xls(self.input_file, sheet=self.args.sheet, encoding_override=self.args.encoding_xls, **kwargs)
            elif filetype == 'xlsx':
                table = agate.Table.from_xlsx(self.input_file, sheet=self.args.sheet, **kwargs)
            elif filetype == 'dbf':
                if not hasattr(self.input_file, 'name'):
                    raise ValueError('DBF files can not be converted from stdin. You must pass a filename.')
                table = agate.Table.from_dbf(self.input_file.name, **kwargs)
            table.to_csv(self.output_file, **self.writer_kwargs)

        if self.args.write_sheets:
            # Close and re-open the file, as the file object has been mutated or closed.
            self.input_file.close()

            self.input_file = self.open_excel_input_file(path)

            if self.args.write_sheets == '-':
                sheets = self.sheet_names(path, filetype)
            elif self.args.regular_expression:
                sheets = [sheet for sheet in self.sheet_names(path, filetype) if re.match(self.args.write_sheets, sheet)]
            else:
                sheets = [int(sheet) if sheet.isdigit() else sheet for sheet in self.args.write_sheets.split(',')]

            if filetype == 'xls':
                tables = agate.Table.from_xls(self.input_file, sheet=sheets, encoding_override=self.args.encoding_xls, **kwargs)
            elif filetype == 'xlsx':
                tables = agate.Table.from_xlsx(self.input_file, sheet=sheets, **kwargs)

            base = splitext(self.input_file.name)[0]
            for i, (sheet_name, table) in enumerate(tables.items()):
                with open('%s_%s.csv' % (base, sheet_name) if self.args.write_sheet_names else '%s_%d.csv' % (base, i), 'w') as f:
                    table.to_csv(f, **self.writer_kwargs)

        self.input_file.close()

        if self.args.schema:
            schema.close()


def launch_new_instance():
    utility = In2CSV()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
