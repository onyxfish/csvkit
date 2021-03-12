#!/usr/bin/env python

import agate

from csvkit.cli import CSVKitUtility


class CSVLook(CSVKitUtility):
    description = 'Render a CSV file in the console as a Markdown-compatible, fixed-width table.'

    def add_arguments(self):
        self.argparser.add_argument('--max-rows', dest='max_rows', type=int,
                                    help='The maximum number of rows to display before truncating the data.')
        self.argparser.add_argument('--max-columns', dest='max_columns', type=int,
                                    help='The maximum number of columns to display before truncating the data.')
        self.argparser.add_argument('--max-column-width', dest='max_column_width', type=int,
                                    help='Truncate all columns to at most this width. The remainder will be replaced with ellipsis.')
        self.argparser.add_argument('-y', '--snifflimit', dest='sniff_limit', type=int, default=1024,
                                    help='Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely.')
        self.argparser.add_argument('-I', '--no-inference', dest='no_inference', action='store_true',
                                    help='Disable type inference when parsing the input.')

    def main(self):
        if self.additional_input_expected():
            self.argparser.error('You must provide an input file or piped data.')

        table = agate.Table.from_csv(
            self.input_file,
            skip_lines=self.args.skip_lines,
            sniff_limit=self.args.sniff_limit,
            column_types=self.get_column_types(),
            line_numbers=self.args.line_numbers,
            **self.reader_kwargs
        )

        table.print_table(
            output=self.output_file,
            max_rows=self.args.max_rows,
            max_columns=self.args.max_columns,
            max_column_width=self.args.max_column_width
        )


def launch_new_instance():
    utility = CSVLook()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
