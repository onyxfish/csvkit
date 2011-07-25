#!/usr/bin/env python

import sys
import StringIO
import unittest

from csvkit import CSVKitReader
from csvkit.utilities.stack import CSVStack

class TestCSVStack(unittest.TestCase):
    def test_explicit_grouping(self):
        # stack two CSV files
        args = ["--groups", "asd,sdf", "-n", "foo", "examples/dummy.csv", "examples/dummy2.csv"]
        output_file = StringIO.StringIO()
        utility = CSVStack(args, output_file)

        utility.main()

        # verify the stacked file's contents
        input_file = StringIO.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(reader.next(), ["foo", "a", "b", "c"])
        self.assertEqual(reader.next()[0], "asd")
        self.assertEqual(reader.next()[0], "sdf")

    def test_filenames_grouping(self):
        # stack two CSV files
        args = ["--filenames", "-n", "path", "examples/dummy.csv", "examples/dummy2.csv"]
        output_file = StringIO.StringIO()
        utility = CSVStack(args, output_file)

        utility.main()

        # verify the stacked file's contents
        input_file = StringIO.StringIO(output_file.getvalue())
        reader = CSVKitReader(input_file)

        self.assertEqual(reader.next(), ["path", "a", "b", "c"])
        self.assertEqual(reader.next()[0], "dummy.csv")
        self.assertEqual(reader.next()[0], "dummy2.csv")

