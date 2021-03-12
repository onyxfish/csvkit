#!/usr/bin/env python

import codecs
from collections import OrderedDict
from decimal import Decimal
import warnings

import agate
from babel.numbers import format_decimal
import six

from csvkit.cli import CSVKitUtility, parse_column_identifiers

NoneType = type(None)

OPERATIONS = OrderedDict([
    ('type', {
        'aggregation': None,
        'label': 'Type of data: '
    }),
    ('nulls', {
        'aggregation': agate.HasNulls,
        'label': 'Contains null values: '
    }),
    ('unique', {
        'aggregation': None,
        'label': 'Unique values: '
    }),
    ('min', {
        'aggregation': agate.Min,
        'label': 'Smallest value: '
    }),
    ('max', {
        'aggregation': agate.Max,
        'label': 'Largest value: '
    }),
    ('sum', {
        'aggregation': agate.Sum,
        'label': 'Sum: '
    }),
    ('mean', {
        'aggregation': agate.Mean,
        'label': 'Mean: '
    }),
    ('median', {
        'aggregation': agate.Median,
        'label': 'Median: '
    }),
    ('stdev', {
        'aggregation': agate.StDev,
        'label': 'StDev: '
    }),
    ('len', {
        'aggregation': agate.MaxLength,
        'label': 'Longest value: '
    }),
    ('freq', {
        'aggregation': None,
        'label': 'Most common values: '
    })
])


class CSVStat(CSVKitUtility):
    description = 'Print descriptive statistics for each column in a CSV file.'
    override_flags = ['L', 'blanks', 'date-format', 'datetime-format']

    def add_arguments(self):
        self.argparser.add_argument('--csv', dest='csv_output', action='store_true',
                                    help='Output results as a CSV, rather than text.')
        self.argparser.add_argument('-n', '--names', dest='names_only', action='store_true',
                                    help='Display column names and indices from the input CSV and exit.')
        self.argparser.add_argument('-c', '--columns', dest='columns',
                                    help='A comma separated list of column indices, names or ranges to be examined, e.g. "1,id,3-5". Defaults to all columns.')
        self.argparser.add_argument('--type', dest='type_only', action='store_true',
                                    help='Only output data type.')
        self.argparser.add_argument('--nulls', dest='nulls_only', action='store_true',
                                    help='Only output whether columns contains nulls.')
        self.argparser.add_argument('--unique', dest='unique_only', action='store_true',
                                    help='Only output counts of unique values.')
        self.argparser.add_argument('--min', dest='min_only', action='store_true',
                                    help='Only output smallest values.')
        self.argparser.add_argument('--max', dest='max_only', action='store_true',
                                    help='Only output largest values.')
        self.argparser.add_argument('--sum', dest='sum_only', action='store_true',
                                    help='Only output sums.')
        self.argparser.add_argument('--mean', dest='mean_only', action='store_true',
                                    help='Only output means.')
        self.argparser.add_argument('--median', dest='median_only', action='store_true',
                                    help='Only output medians.')
        self.argparser.add_argument('--stdev', dest='stdev_only', action='store_true',
                                    help='Only output standard deviations.')
        self.argparser.add_argument('--len', dest='len_only', action='store_true',
                                    help='Only output the length of the longest values.')
        self.argparser.add_argument('--freq', dest='freq_only', action='store_true',
                                    help='Only output lists of frequent values.')
        self.argparser.add_argument('--freq-count', dest='freq_count', type=int,
                                    help='The maximum number of frequent values to display.')
        self.argparser.add_argument('--count', dest='count_only', action='store_true',
                                    help='Only output total row count.')
        self.argparser.add_argument('-y', '--snifflimit', dest='sniff_limit', type=int, default=1024,
                                    help='Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely.')

    def main(self):
        if self.args.names_only:
            self.print_column_names()
            return

        if self.additional_input_expected():
            self.argparser.error('You must provide an input file or piped data.')

        operations = [op for op in OPERATIONS.keys() if getattr(self.args, op + '_only')]

        if len(operations) > 1:
            self.argparser.error('Only one operation argument may be specified (--mean, --median, etc).')

        if operations and self.args.csv_output:
            self.argparser.error('You may not specify --csv and an operation (--mean, --median, etc) at the same time.')

        if operations and self.args.count_only:
            self.argparser.error('You may not specify --count and an operation (--mean, --median, etc) at the same time.')

        if six.PY2:
            self.output_file = codecs.getwriter('utf-8')(self.output_file)

        if self.args.count_only:
            count = len(list(agate.csv.reader(self.skip_lines(), **self.reader_kwargs)))

            if not self.args.no_header_row:
                count -= 1

            self.output_file.write('%i\n' % count)

            return

        table = agate.Table.from_csv(
            self.input_file,
            skip_lines=self.args.skip_lines,
            sniff_limit=self.args.sniff_limit,
            **self.reader_kwargs
        )

        column_ids = parse_column_identifiers(
            self.args.columns,
            table.column_names,
            self.get_column_offset()
        )

        kwargs = {}

        if self.args.freq_count:
            kwargs['freq_count'] = self.args.freq_count

        # Output a single stat
        if operations:
            if len(column_ids) == 1:
                self.print_one(table, column_ids[0], operations[0], label=False, **kwargs)
            else:
                for column_id in column_ids:
                    self.print_one(table, column_id, operations[0], **kwargs)
        else:
            stats = {}

            for column_id in column_ids:
                stats[column_id] = self.calculate_stats(table, column_id, **kwargs)

            # Output as CSV
            if self.args.csv_output:
                self.print_csv(table, column_ids, stats)
            # Output all stats
            else:
                self.print_stats(table, column_ids, stats)

    def is_finite_decimal(self, value):
        return isinstance(value, Decimal) and value.is_finite()

    def print_one(self, table, column_id, operation, label=True, **kwargs):
        """
        Print data for a single statistic.
        """
        column_name = table.column_names[column_id]

        op_name = operation
        getter = globals().get('get_%s' % op_name, None)

        with warnings.catch_warnings():
            warnings.simplefilter('ignore', agate.NullCalculationWarning)

            try:
                if getter:
                    stat = getter(table, column_id, **kwargs)
                else:
                    op = OPERATIONS[op_name]['aggregation']
                    stat = table.aggregate(op(column_id))

                    if self.is_finite_decimal(stat):
                        stat = format_decimal(stat, locale=agate.config.get_option('default_locale'))
            except:
                stat = None

        # Formatting
        if op_name == 'freq':
            stat = ', '.join([(u'"%s": %s' % (six.text_type(row[column_name]), row['Count'])) for row in stat])
            stat = u'{ %s }' % stat

        if label:
            self.output_file.write(u'%3i. %s: %s\n' % (column_id + 1, column_name, stat))
        else:
            self.output_file.write(u'%s\n' % stat)

    def calculate_stats(self, table, column_id, **kwargs):
        """
        Calculate stats for all valid operations.
        """
        stats = {}

        for op_name, op_data in OPERATIONS.items():
            getter = globals().get('get_%s' % op_name, None)

            with warnings.catch_warnings():
                warnings.simplefilter('ignore', agate.NullCalculationWarning)

                try:
                    if getter:
                        stats[op_name] = getter(table, column_id, **kwargs)
                    else:
                        op = op_data['aggregation']
                        v = table.aggregate(op(column_id))

                        if self.is_finite_decimal(v):
                            v = format_decimal(v, locale=agate.config.get_option('default_locale'))

                        stats[op_name] = v
                except:
                    stats[op_name] = None

        return stats

    def print_stats(self, table, column_ids, stats):
        """
        Print data for all statistics.
        """
        label_column_width = max([len(op_data['label']) for op_data in OPERATIONS.values()])

        for column_id in column_ids:
            column_name = table.column_names[column_id]
            column = table.columns[column_id]
            column_stats = stats[column_id]

            self.output_file.write(('%3i. "%s"\n\n' % (column_id + 1, column_name)))

            for op_name, op_data in OPERATIONS.items():
                if column_stats[op_name] is None:
                    continue

                label = u'{label:{label_column_width}}'.format(**{
                    'label_column_width': label_column_width,
                    'label': op_data['label']
                })

                if op_name == 'freq':
                    for i, row in enumerate(column_stats['freq']):
                        if i == 0:
                            self.output_file.write('\t{} '.format(label))
                        else:
                            self.output_file.write(u'\t{label:{label_column_width}} '.format(**{
                                'label_column_width': label_column_width,
                                'label': ''
                            }))

                        if isinstance(column.data_type, agate.Number):
                            v = row[column_name]

                            if self.is_finite_decimal(v):
                                v = format_decimal(v, locale=agate.config.get_option('default_locale'))
                        else:
                            v = six.text_type(row[column_name])

                        self.output_file.write(u'{} ({}x)\n'.format(v, row['Count']))

                    continue

                v = column_stats[op_name]

                if op_name == 'nulls' and v:
                    v = '%s (excluded from calculations)' % v
                elif op_name == 'len':
                    v = '%s characters' % v

                self.output_file.write(u'\t{} {}\n'.format(label, v))

            self.output_file.write('\n')

        self.output_file.write('Row count: %s\n' % len(table.rows))

    def print_csv(self, table, column_ids, stats):
        """
        Print data for all statistics as a csv table.
        """
        writer = agate.csv.writer(self.output_file)

        header = ['column_id', 'column_name'] + [op_name for op_name in OPERATIONS.keys()]

        writer.writerow(header)

        for column_id in column_ids:
            column_name = table.column_names[column_id]
            column_stats = stats[column_id]

            output_row = [column_id + 1, column_name]

            for op_name, op_data in OPERATIONS.items():
                if column_stats[op_name] is None:
                    output_row.append(None)
                    continue

                if op_name == 'freq':
                    value = ', '.join([six.text_type(row[column_name]) for row in column_stats['freq']])
                else:
                    value = column_stats[op_name]

                output_row.append(value)

            writer.writerow(output_row)


def get_type(table, column_id, **kwargs):
    return '%s' % table.columns[column_id].data_type.__class__.__name__


def get_unique(table, column_id, **kwargs):
    return len(table.columns[column_id].values_distinct())


def get_freq(table, column_id, freq_count=5, **kwargs):
    return table.pivot(column_id).order_by('Count', reverse=True).limit(freq_count)


def launch_new_instance():
    utility = CSVStat()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
