#!/usr/bin/env python

import sys

import agate

from csvkit.cli import CSVKitUtility


class CSVFormat(CSVKitUtility):
    description = 'Convert a CSV file to a custom output format.'
    override_flags = ['blanks', 'date-format', 'datetime-format']

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
        if self.additional_input_expected():
            sys.stderr.write('No input file or piped data provided. Waiting for standard input:\n')

        if self.args.out_quoting == 2:
            self.args.infer_only_numbers = True
        else:
            self.args.no_inference = True
        self.reader_kwargs['column_types'] = self.get_column_types()

        table = agate.Table.from_csv(self.skip_lines(), **self.reader_kwargs)
        writer = agate.csv.writer(self.output_file, **self.writer_kwargs)
        if not self.args.no_header_row:
            writer.writerow(table.column_names)
        writer.writerows(table.rows)


def launch_new_instance():
    utility = CSVFormat()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
