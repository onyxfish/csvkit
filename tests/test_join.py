#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from csvkit import join


class TestJoin(unittest.TestCase):

    def setUp(self):
        self.tab1 = [
            ['id', 'name', 'i_work_here'],
            [u'1', u'Chicago Reader', u'first'],
            [u'2', u'Chicago Sun-Times', u'only'],
            [u'3', u'Chicago Tribune', u'only'],
            [u'1', u'Chicago Reader', u'second']]

        self.tab2 = [
            ['id', 'age', 'i_work_here'],
            [u'1', u'first', u'0'],
            [u'4', u'only', u'0'],
            [u'1', u'second', u'0'],
            [u'2', u'only', u'0', u'0']]  # Note extra value in this column

    def test_get_keys(self):
        self.assertEqual(join._get_keys(self.tab1[1:], 0).keys(), set([u'1', u'2', u'3', u'1']))
        self.assertEqual(join._get_keys(self.tab2[1:], 0).keys(), set([u'1', u'4', u'1', u'2']))

    def test_get_mapped_keys(self):
        self.assertEqual(join._get_mapped_keys(self.tab1[1:], 0), {
            u'1': [[u'1', u'Chicago Reader', u'first'], [u'1', u'Chicago Reader', u'second']],
            u'2': [[u'2', u'Chicago Sun-Times', u'only']],
            u'3': [[u'3', u'Chicago Tribune', u'only']]})

    def test_get_mapped_keys_ignore_case(self):
        mapped_keys = join._get_mapped_keys(self.tab1[1:], 1, case_insensitive=True)
        assert u'Chicago Reader' in mapped_keys
        assert u'chicago reader' in mapped_keys
        assert u'CHICAGO SUN-TIMES' in mapped_keys
        assert u'1' not in mapped_keys

    def test_sequential_join(self):
        self.assertEqual(join.sequential_join(self.tab1, self.tab2), [
            ['id', 'name', 'i_work_here', 'id', 'age', 'i_work_here'],
            [u'1', u'Chicago Reader', u'first', u'1', u'first', u'0'],
            [u'2', u'Chicago Sun-Times', u'only', u'4', u'only', u'0'],
            [u'3', u'Chicago Tribune', u'only', u'1', u'second', u'0'],
            [u'1', u'Chicago Reader', u'second', u'2', u'only', u'0', u'0']])

    def test_inner_join(self):
        self.assertEqual(join.inner_join(self.tab1, 0, self.tab2, 0), [
            ['id', 'name', 'i_work_here', 'id', 'age', 'i_work_here'],
            [u'1', u'Chicago Reader', u'first', u'1', u'first', u'0'],
            [u'1', u'Chicago Reader', u'first', u'1', u'second', u'0'],
            [u'2', u'Chicago Sun-Times', u'only', u'2', u'only', u'0', u'0'],
            [u'1', u'Chicago Reader', u'second', u'1', u'first', u'0'],
            [u'1', u'Chicago Reader', u'second', u'1', u'second', u'0']])

    def test_full_outer_join(self):
        self.assertEqual(join.full_outer_join(self.tab1, 0, self.tab2, 0), [
            ['id', 'name', 'i_work_here', 'id', 'age', 'i_work_here'],
            [u'1', u'Chicago Reader', u'first', u'1', u'first', u'0'],
            [u'1', u'Chicago Reader', u'first', u'1', u'second', u'0'],
            [u'2', u'Chicago Sun-Times', u'only', u'2', u'only', u'0', u'0'],
            [u'3', u'Chicago Tribune', u'only', u'', u'', u''],
            [u'1', u'Chicago Reader', u'second', u'1', u'first', u'0'],
            [u'1', u'Chicago Reader', u'second', u'1', u'second', u'0'],
            [u'', u'', u'', u'4', u'only', u'0']])

    def test_left_outer_join(self):
        self.assertEqual(join.left_outer_join(self.tab1, 0, self.tab2, 0), [
            ['id', 'name', 'i_work_here', 'id', 'age', 'i_work_here'],
            [u'1', u'Chicago Reader', u'first', u'1', u'first', u'0'],
            [u'1', u'Chicago Reader', u'first', u'1', u'second', u'0'],
            [u'2', u'Chicago Sun-Times', u'only', u'2', u'only', u'0', u'0'],
            [u'3', u'Chicago Tribune', u'only', u'', u'', u''],
            [u'1', u'Chicago Reader', u'second', u'1', u'first', u'0'],
            [u'1', u'Chicago Reader', u'second', u'1', u'second', u'0']])

    def test_right_outer_join(self):
        self.assertEqual(join.right_outer_join(self.tab1, 0, self.tab2, 0), [
            ['id', 'name', 'i_work_here', 'id', 'age', 'i_work_here'],
            [u'1', u'Chicago Reader', u'first', u'1', u'first', u'0'],
            [u'1', u'Chicago Reader', u'first', u'1', u'second', u'0'],
            [u'2', u'Chicago Sun-Times', u'only', u'2', u'only', u'0', u'0'],
            [u'1', u'Chicago Reader', u'second', u'1', u'first', u'0'],
            [u'1', u'Chicago Reader', u'second', u'1', u'second', u'0'],
            [u'', u'', u'', u'4', u'only', u'0']])

    def test_right_outer_join_ignore_case(self):
        # Right outer join exercises all the case dependencies
        tab1 = [
            ['id', 'name', 'i_work_here'],
            [u'a', u'Chicago Reader', u'first'],
            [u'b', u'Chicago Sun-Times', u'only'],
            [u'c', u'Chicago Tribune', u'only'],
            [u'a', u'Chicago Reader', u'second']]

        tab2 = [
            ['id', 'age', 'i_work_here'],
            [u'A', u'first', u'0'],
            [u'D', u'only', u'0'],
            [u'A', u'second', u'0'],
            [u'B', u'only', u'0', u'0']]  # Note extra value in this column

        self.assertEqual(join.right_outer_join(tab1, 0, tab2, 0, ignore_case=True), [
                ['id', 'name', 'i_work_here', 'id', 'age', 'i_work_here'],
                [u'a', u'Chicago Reader', u'first', u'A', u'first', u'0'],
                [u'a', u'Chicago Reader', u'first', u'A', u'second', u'0'],
                [u'b', u'Chicago Sun-Times', u'only', u'B', u'only', u'0', u'0'],
                [u'a', u'Chicago Reader', u'second', u'A', u'first', u'0'],
                [u'a', u'Chicago Reader', u'second', u'A', u'second', u'0'],
                [u'', u'', u'', u'D', u'only', u'0']])
