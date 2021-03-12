#!/usr/bin/env python

import codecs
import datetime
import decimal
import sys

try:
    from collections import OrderedDict
    import json
except ImportError:
    from ordereddict import OrderedDict
    import simplejson as json

import agate
import six

from csvkit.cli import CSVKitUtility, match_column_identifier


class CSVJSON(CSVKitUtility):
    description = 'Convert a CSV file into JSON (or GeoJSON).'

    def add_arguments(self):
        self.argparser.add_argument('-i', '--indent', dest='indent', type=int,
                                    help='Indent the output JSON this many spaces. Disabled by default.')
        self.argparser.add_argument('-k', '--key', dest='key',
                                    help='Output JSON as an array of objects keyed by a given column, KEY, rather than as a list. All values in the column must be unique. If --lat and --lon are also specified, this column will be used as GeoJSON Feature ID.')
        self.argparser.add_argument('--lat', dest='lat',
                                    help='A column index or name containing a latitude. Output will be GeoJSON instead of JSON. Only valid if --lon is also specified.')
        self.argparser.add_argument('--lon', dest='lon',
                                    help='A column index or name containing a longitude. Output will be GeoJSON instead of JSON. Only valid if --lat is also specified.')
        self.argparser.add_argument('--type', dest='type',
                                    help='A column index or name containing a GeoJSON type. Output will be GeoJSON instead of JSON. Only valid if --lat and --lon are also specified.')
        self.argparser.add_argument('--geometry', dest='geometry',
                                    help='A column index or name containing a GeoJSON geometry. Output will be GeoJSON instead of JSON. Only valid if --lat and --lon are also specified.')
        self.argparser.add_argument('--crs', dest='crs',
                                    help='A coordinate reference system string to be included with GeoJSON output. Only valid if --lat and --lon are also specified.')
        self.argparser.add_argument('--no-bbox', dest='no_bbox', action='store_true',
                                    help='Disable the calculation of a bounding box.')
        self.argparser.add_argument('--stream', dest='streamOutput', action='store_true',
                                    help='Output JSON as a stream of newline-separated objects, rather than an as an array.')
        self.argparser.add_argument('-y', '--snifflimit', dest='sniff_limit', type=int, default=1024,
                                    help='Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely.')
        self.argparser.add_argument('-I', '--no-inference', dest='no_inference', action='store_true',
                                    help='Disable type inference (and --locale, --date-format, --datetime-format) when parsing CSV input.')

    def __init__(self, args=None, output_file=None):
        super(CSVJSON, self).__init__(args, output_file)

        self.validate_args()

        self.json_kwargs = {
            'ensure_ascii': False,
            'indent': self.args.indent,
        }

        # We need to do this stream dance here, because we aren't writing through agate.
        if six.PY2:
            self.stream = codecs.getwriter('utf-8')(self.output_file)
            self.json_kwargs['encoding'] = 'utf-8'
        else:
            self.stream = self.output_file

    def main(self):
        """
        Convert CSV to JSON.
        """

        if self.can_stream():
            if self.additional_input_expected():
                sys.stderr.write('No input file or piped data provided. Waiting for standard input:\n')

            if self.is_geo():
                self.streaming_output_ndgeojson()
            else:
                self.streaming_output_ndjson()

        else:
            if self.additional_input_expected():
                self.argparser.error('You must provide an input file or piped data.')

            if self.is_geo():
                self.output_geojson()
            else:
                self.output_json()

    def dump_json(self, data, newline=False):
        def default(obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()
            elif isinstance(obj, decimal.Decimal):
                return str(obj)
            raise TypeError('%s is not JSON serializable' % repr(obj))

        json.dump(data, self.stream, default=default, **self.json_kwargs)
        if newline:
            self.stream.write("\n")

    def can_stream(self):
        return self.args.streamOutput and self.args.no_inference and self.args.sniff_limit == 0 and not self.args.skip_lines

    def is_geo(self):
        return self.args.lat and self.args.lon

    def validate_args(self):
        if self.args.lat and not self.args.lon:
            self.argparser.error('--lon is required whenever --lat is specified.')
        if self.args.lon and not self.args.lat:
            self.argparser.error('--lat is required whenever --lon is specified.')

        if self.args.crs and not self.args.lat:
            self.argparser.error('--crs is only allowed when --lat and --lon are also specified.')
        if self.args.type and not self.args.lat:
            self.argparser.error('--type is only allowed when --lat and --lon are also specified.')
        if self.args.geometry and not self.args.lat:
            self.argparser.error('--geometry is only allowed when --lat and --lon are also specified.')

        if self.args.key and self.args.streamOutput and not (self.args.lat and self.args.lon):
            self.argparser.error('--key is only allowed with --stream when --lat and --lon are also specified.')

    def read_csv_to_table(self):
        return agate.Table.from_csv(
            self.input_file,
            skip_lines=self.args.skip_lines,
            sniff_limit=self.args.sniff_limit,
            column_types=self.get_column_types(),
            **self.reader_kwargs
        )

    def output_json(self):
        self.read_csv_to_table().to_json(
            self.output_file,
            key=self.args.key,
            newline=self.args.streamOutput,
            indent=self.args.indent,
        )

    def output_geojson(self):
        table = self.read_csv_to_table()
        geojson_generator = self.GeoJsonGenerator(self.args, table.column_names)

        if self.args.streamOutput:
            for row in table.rows:
                self.dump_json(geojson_generator.feature_for_row(row), newline=True)
        else:
            self.dump_json(geojson_generator.generate_feature_collection(table))

    def streaming_output_ndjson(self):
        rows = agate.csv.reader(self.input_file, **self.reader_kwargs)
        column_names = next(rows)

        for row in rows:
            data = OrderedDict()
            for i, column in enumerate(column_names):
                try:
                    data[column] = row[i]
                except IndexError:
                    data[column] = None
            self.dump_json(data, newline=True)

    def streaming_output_ndgeojson(self):
        rows = agate.csv.reader(self.input_file, **self.reader_kwargs)
        column_names = next(rows)
        geojson_generator = self.GeoJsonGenerator(self.args, column_names)

        for row in rows:
            self.dump_json(geojson_generator.feature_for_row(row), newline=True)

    class GeoJsonGenerator:
        def __init__(self, args, column_names):
            self.args = args
            self.column_names = column_names

            self.lat_column = match_column_identifier(column_names, self.args.lat, self.args.zero_based)

            self.lon_column = match_column_identifier(column_names, self.args.lon, self.args.zero_based)

            if self.args.type:
                self.type_column = match_column_identifier(column_names, self.args.type, self.args.zero_based)
            else:
                self.type_column = None

            if self.args.geometry:
                self.geometry_column = match_column_identifier(column_names, self.args.geometry, self.args.zero_based)
            else:
                self.geometry_column = None

            if self.args.key:
                self.id_column = match_column_identifier(column_names, self.args.key, self.args.zero_based)
            else:
                self.id_column = None

        def generate_feature_collection(self, table):
            features = []
            bounds = self.GeoJsonBounds()

            for row in table.rows:
                feature = self.feature_for_row(row)

                if not self.args.no_bbox:
                    bounds.add_feature(feature)

                features.append(feature)

            items = [
                ('type', 'FeatureCollection'),
                ('features', features),
            ]

            if not self.args.no_bbox:
                items.insert(1, ('bbox', bounds.bbox()))

            if self.args.crs:
                items.append(('crs', OrderedDict([
                    ('type', 'name'),
                    ('properties', {
                        'name': self.args.crs,
                    }),
                ])))

            return OrderedDict(items)

        def feature_for_row(self, row):
            feature = OrderedDict([
                ('type', 'Feature'),
                ('properties', OrderedDict()),
            ])

            for i, c in enumerate(row):
                # Prevent "type" or geo fields from being added to properties.
                if c is None or i in (self.type_column, self.lat_column, self.lon_column, self.geometry_column):
                    continue
                elif i == self.id_column:
                    feature['id'] = c
                elif c:
                    feature['properties'][self.column_names[i]] = c

            feature['geometry'] = self.geometry_for_row(row)

            return feature

        def geometry_for_row(self, row):
            lat = None
            lon = None

            if self.geometry_column is not None:
                return json.loads(row[self.geometry_column])

            if self.lat_column is not None and self.lon_column is not None:
                try:
                    lon = float(row[self.lon_column])
                    lat = float(row[self.lat_column])
                except ValueError:
                    lon = None
                    lat = None

            if lon and lat:
                return OrderedDict([
                    ('type', 'Point'),
                    ('coordinates', [lon, lat]),
                ])

        class GeoJsonBounds:
            def __init__(self):
                self.min_lon = None
                self.min_lat = None
                self.max_lon = None
                self.max_lat = None

            def bbox(self):
                return [self.min_lon, self.min_lat, self.max_lon, self.max_lat]

            def add_feature(self, feature):
                if 'geometry' in feature and 'coordinates' in feature['geometry']:
                    self.update_coordinates(feature['geometry']['coordinates'])

            def update_lat(self, lat):
                if self.min_lat is None or lat < self.min_lat:
                    self.min_lat = lat
                if self.max_lat is None or lat > self.max_lat:
                    self.max_lat = lat

            def update_lon(self, lon):
                if self.min_lon is None or lon < self.min_lon:
                    self.min_lon = lon
                if self.max_lon is None or lon > self.max_lon:
                    self.max_lon = lon

            def update_coordinates(self, coordinates):
                if len(coordinates) <= 3 and isinstance(coordinates[0], (float, int)):
                    self.update_lon(coordinates[0])
                    self.update_lat(coordinates[1])
                else:
                    for coordinate in coordinates:
                        self.update_coordinates(coordinate)


def launch_new_instance():
    utility = CSVJSON()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
