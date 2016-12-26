#!/usr/bin/env python

import agate

from csvkit import join
from csvkit.cli import CSVKitUtility, match_column_identifier


class CSVJoin(CSVKitUtility):
    description = 'Execute a SQL-like join to merge CSV files on a specified column or columns.'
    epilog = 'Note that the join operation requires reading all files into memory. Don\'t try this on very large files.'
    override_flags = ['f']

    def add_arguments(self):
        self.argparser.add_argument(metavar="FILE", nargs='*', dest='input_paths', default=['-'],
                                    help='The CSV files to operate on. If only one is specified, it will be copied to STDOUT.')
        self.argparser.add_argument('-c', '--columns', dest='columns',
                                    help='The column name(s) on which to join. Should be either one name (or index) or a comma-separated list with one name (or index) for each file, in the same order that the files were specified. May also be left unspecified, in which case the two files will be joined sequentially without performing any matching.')
        self.argparser.add_argument('--outer', dest='outer_join', action='store_true',
                                    help='Perform a full outer join, rather than the default inner join.')
        self.argparser.add_argument('--left', dest='left_join', action='store_true',
                                    help='Perform a left outer join, rather than the default inner join. If more than two files are provided this will be executed as a sequence of left outer joins, starting at the left.')
        self.argparser.add_argument('--right', dest='right_join', action='store_true',
                                    help='Perform a right outer join, rather than the default inner join. If more than two files are provided this will be executed as a sequence of right outer joins, starting at the right.')
        self.argparser.add_argument('--ignorecase', dest='ignore_case', action='store_true',
                                    help='Whether to ignore string case when comparing keys.')

    def main(self):
        self.input_files = []

        for path in self.args.input_paths:
            self.input_files.append(self._open_input_file(path))

        if len(self.input_files) < 2:
            self.argparser.error('You must specify at least two files to join.')

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
        header = not self.args.no_header_row

        for f in self.input_files:
            tables.append(list(agate.csv.reader(f, header=header, **self.reader_kwargs)))
            f.close()

        join_column_ids = []

        if self.args.columns:
            for i, t in enumerate(tables):
                join_column_ids.append(match_column_identifier(t[0], join_column_names[i]))

        jointab = tables[0]

        ignore_case = self.args.ignore_case
        if self.args.left_join:
            # Left outer join
            for i, t in enumerate(tables[1:]):
                jointab = join.left_outer_join(jointab, join_column_ids[0], t, join_column_ids[i + 1], header=header, ignore_case=ignore_case)
        elif self.args.right_join:
            # Right outer join
            jointab = tables[-1]

            remaining_tables = tables[:-1]
            remaining_tables.reverse()

            for i, t in enumerate(remaining_tables):
                jointab = join.right_outer_join(t, join_column_ids[-(i + 2)], jointab, join_column_ids[-1], header=header, ignore_case=ignore_case)
        elif self.args.outer_join:
            # Full outer join
            for i, t in enumerate(tables[1:]):
                jointab = join.full_outer_join(jointab, join_column_ids[0], t, join_column_ids[i + 1], header=header, ignore_case=ignore_case)
        elif self.args.columns:
            # Inner join
            for i, t in enumerate(tables[1:]):
                jointab = join.inner_join(jointab, join_column_ids[0], t, join_column_ids[i + 1], header=header, ignore_case=ignore_case)
        else:
            # Sequential join
            for t in tables[1:]:
                jointab = join.sequential_join(jointab, t, header=header)

        output = agate.csv.writer(self.output_file, **self.writer_kwargs)

        for row in jointab:
            output.writerow(row)

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
