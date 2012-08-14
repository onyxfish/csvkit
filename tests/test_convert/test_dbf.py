#!/usr/bin/env python

import unittest

from csvkit.convert import dbase

class TestDBF(unittest.TestCase):
    def setUp(self):
        dbase.dbf.input_decoding = 'utf-8'

    def test_dbf(self):
        with open('examples/testdbf.dbf', 'rb') as f:
            output = dbase.dbf2csv(f)

        with open('examples/testdbf_converted.csv', 'r') as f:
            self.assertEquals(f.read(), output)

