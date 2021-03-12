#!/usr/bin/env python

import agate

from csvkit.cli import CSVKitUtility, match_column_identifier


class CSVJoin(CSVKitUtility):
    description = 'Execute a SQL-like join to merge CSV files on a specified column or columns.'
    epilog = 'Note that the join operation requires reading all files into memory. Don\'t try this on very large files.'
    # Override 'f' because the utility accepts multiple files.
    override_flags = ['f']

    def add_arguments(self):
        self.argparser.add_argument(metavar='FILE', nargs='*', dest='input_paths', default=['-'],
                                    help='The CSV files to operate on. If only one is specified, it will be copied to STDOUT.')
        self.argparser.add_argument('-c', '--columns', dest='columns',
                                    help='The column name(s) on which to join. Should be either one name (or index) or a comma-separated list with one name (or index) for each file, in the same order that the files were specified. May also be left unspecified, in which case the two files will be joined sequentially without performing any matching.')
        self.argparser.add_argument('--outer', dest='outer_join', action='store_true',
                                    help='Perform a full outer join, rather than the default inner join.')
        self.argparser.add_argument('--left', dest='left_join', action='store_true',
                                    help='Perform a left outer join, rather than the default inner join. If more than two files are provided this will be executed as a sequence of left outer joins, starting at the left.')
        self.argparser.add_argument('--right', dest='right_join', action='store_true',
                                    help='Perform a right outer join, rather than the default inner join. If more than two files are provided this will be executed as a sequence of right outer joins, starting at the right.')
        self.argparser.add_argument('-y', '--snifflimit', dest='sniff_limit', type=int, default=1024,
                                    help='Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely.')
        self.argparser.add_argument('-I', '--no-inference', dest='no_inference', action='store_true',
                                    help='Disable type inference when parsing CSV input.')

    def main(self):
        self.input_files = []

        for path in self.args.input_paths:
            self.input_files.append(self._open_input_file(path))

        if len(self.input_files) < 1:
            self.argparser.error('You must specify at least one file to join.')

        if self.args.columns:
            join_column_names = self._parse_join_column_names(self.args.columns)

            if len(join_column_names) == 1:
                join_column_names = join_column_names * len(self.input_files)

            if len(join_column_names) != len(self.input_files):
                self.argparser.error('The number of join column names must match the number of files, or be a single column name that exists in all files.')

        if (self.args.left_join or self.args.right_join or self.args.outer_join) and not self.args.columns:
            self.argparser.error('You must provide join column names when performing an outer join.')

        if self.args.left_join and self.args.right_join:
            self.argparser.error('It is not valid to specify both a left and a right join.')

        tables = []
        sniff_limit = self.args.sniff_limit
        column_types = self.get_column_types()

        for f in self.input_files:
            tables.append(agate.Table.from_csv(
                f,
                skip_lines=self.args.skip_lines,
                sniff_limit=sniff_limit,
                column_types=column_types,
                **self.reader_kwargs
            ))
            f.close()

        join_column_ids = []

        if self.args.columns:
            for i, table in enumerate(tables):
                join_column_ids.append(match_column_identifier(table.column_names, join_column_names[i]))

        jointab = tables[0]

        if self.args.left_join:
            # Left outer join
            for i, table in enumerate(tables[1:]):
                jointab = agate.Table.join(jointab, table, join_column_ids[0], join_column_ids[i + 1])
        elif self.args.right_join:
            # Right outer join
            jointab = tables[-1]

            remaining_tables = tables[:-1]
            remaining_tables.reverse()

            for i, table in enumerate(remaining_tables):
                jointab = agate.Table.join(jointab, table, join_column_ids[-(i + 2)], join_column_ids[-1])
        elif self.args.outer_join:
            # Full outer join
            for i, table in enumerate(tables[1:]):
                jointab = agate.Table.join(jointab, table, join_column_ids[0], join_column_ids[i + 1], full_outer=True)
        elif self.args.columns:
            # Inner join
            for i, table in enumerate(tables[1:]):
                jointab = agate.Table.join(jointab, table, join_column_ids[0], join_column_ids[i + 1], inner=True)
        else:
            # Sequential join
            for table in tables[1:]:
                jointab = agate.Table.join(jointab, table, full_outer=True)

        jointab.to_csv(self.output_file, **self.writer_kwargs)

    def _parse_join_column_names(self, join_string):
        """
        Parse a list of join columns.
        """
        return list(map(str.strip, join_string.split(',')))


def launch_new_instance():
    utility = CSVJoin()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
