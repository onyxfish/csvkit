#!/usr/bin/env python

import csv
from decimal import Decimal, InvalidOperation
import io
import sys

import agate
import six

from csvkit.cli import CSVKitUtility


class CSVFormat(CSVKitUtility):
    description = 'Convert a CSV file to a custom output format.'
    override_flags = ['L', 'blanks', 'date-format', 'datetime-format']

    def add_arguments(self):
        self.argparser.add_argument('-D', '--out-delimiter', dest='out_delimiter',
                                    help='Delimiting character of the output CSV file.')
        self.argparser.add_argument('-T', '--out-tabs', dest='out_tabs', action='store_true',
                                    help='Specify that the output CSV file is delimited with tabs. Overrides "-D".')
        self.argparser.add_argument('-Q', '--out-quotechar', dest='out_quotechar',
                                    help='Character used to quote strings in the output CSV file.')
        self.argparser.add_argument('-U', '--out-quoting', dest='out_quoting', type=int, choices=[0, 1, 2, 3],
                                    help='Quoting style used in the output CSV file. 0 = Quote Minimal, 1 = Quote All, 2 = Quote Non-numeric, 3 = Quote None.')
        self.argparser.add_argument('-B', '--out-no-doublequote', dest='out_doublequote', action='store_false',
                                    help='Whether or not double quotes are doubled in the output CSV file.')
        self.argparser.add_argument('-P', '--out-escapechar', dest='out_escapechar',
                                    help='Character used to escape the delimiter in the output CSV file if --quoting 3 ("Quote None") is specified and to escape the QUOTECHAR if --no-doublequote is specified.')
        self.argparser.add_argument('-M', '--out-lineterminator', dest='out_lineterminator',
                                    help='Character used to terminate lines in the output CSV file.')

    def _extract_csv_writer_kwargs(self):
        kwargs = {}

        if self.args.line_numbers:
            kwargs['line_numbers'] = True

        if self.args.out_tabs:
            kwargs['delimiter'] = '\t'
        elif self.args.out_delimiter:
            kwargs['delimiter'] = self.args.out_delimiter

        for arg in ('quotechar', 'quoting', 'doublequote', 'escapechar', 'lineterminator'):
            value = getattr(self.args, 'out_%s' % arg)
            if value is not None:
                kwargs[arg] = value

        return kwargs

    def main(self):
        if six.PY2:
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr)

        if self.additional_input_expected():
            sys.stderr.write('No input file or piped data provided. Waiting for standard input:\n')

        input_file = self.skip_lines()

        # When using -U 2 (QUOTE_NONNUMERIC), we have to know which columns are numeric in the input file, to avoid quoting them in the output.
        # If the input file is not in the same QUOTE_NONNUMERIC quoting format, the reader cannot determine which columns are numeric;
        # we'll have to lend it a hand, but it will be much slower and memory-consuming, so we make this a special case.
        detect_numeric_columns = False
        numeric_columns = []
        if 'quoting' in self.writer_kwargs and self.writer_kwargs['quoting'] == csv.QUOTE_NONNUMERIC:
            if 'quoting' not in self.reader_kwargs or self.reader_kwargs['quoting'] != csv.QUOTE_NONNUMERIC:
                detect_numeric_columns = True

        # Find out which columns are numeric if this is required
        if detect_numeric_columns:
            # We create a dumb TypeTester to avoid converting null values detected by agate
            def DumbTypeTester():
                # We get agate's normal possible types
                types = agate.TypeTester()._possible_types
                for i, t in enumerate(types):
                    types[i] = t.__class__(null_values=('',))
                return agate.TypeTester(types=types)
            # We now load the file's contents in a Table and get which columns contain Numbers
            input_data = input_file.read() # we need to cache the file's contents to use it twice
            input_file = io.StringIO(input_data)
            table = agate.Table.from_csv(input_file, column_types=DumbTypeTester(), **self.reader_kwargs)
            numeric_columns = [n for n in range(0, len(table.column_types)) if isinstance(table.column_types[n], agate.Number)]
            input_file = io.StringIO(input_data) # reload it from the cache for use by the csv reader

        # Read and write CSV
        reader = agate.csv.reader(input_file, **self.reader_kwargs)
        writer = agate.csv.writer(self.output_file, **self.writer_kwargs)
        if detect_numeric_columns:
            # Special case where we need to convert numeric columns from strings to decimals
            if 'header' not in self.reader_kwargs or self.reader_kwargs['header']:
                writer.writerow(next(reader))
            for row in reader:
                try:
                    writer.writerow([Decimal(row[n]) if n in numeric_columns and row[n] != '' else row[n] for n in range(0, len(row))])
                except InvalidOperation as e:
                    sys.stderr.write(f"Error on line {reader.line_num} ")
                    for n in numeric_columns:
                        try:
                            if row[n] != '':
                                d = Decimal(row[n])
                        except InvalidOperation:
                            sys.stderr.write(f"in column {n}: '{row[n]}' cannot be converted to Decimal.\n")
                            raise e
        else:
            # The usual and much quicker case: pipe from the reader to the writer
            writer.writerows(reader)


def launch_new_instance():
    utility = CSVFormat()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
