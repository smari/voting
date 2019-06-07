import math
import unittest

from apportion import apportion1d
from division_rules import dhondt_gen, sainte_lague_gen, \
    nordic_sainte_lague_gen, imperiali_gen, danish_gen, huntington_hill_gen

class TestDivisors(unittest.TestCase):

    def test_dhondt(self):
        gen = dhondt_gen()
        first = next(gen)
        base = first
        self.assertEqual(first,     1*base)
        self.assertEqual(next(gen), 2*base)
        self.assertEqual(next(gen), 3*base)
        self.assertEqual(next(gen), 4*base)
        self.assertEqual(next(gen), 5*base)

    def test_lague(self):
        gen = sainte_lague_gen()
        first = next(gen)
        base = first
        self.assertEqual(first,     1*base)
        self.assertEqual(next(gen), 3*base)
        self.assertEqual(next(gen), 5*base)
        self.assertEqual(next(gen), 7*base)
        self.assertEqual(next(gen), 9*base)

    def test_nordic_lague(self):
        gen = nordic_sainte_lague_gen()
        first = next(gen)
        second = next(gen)
        base = second/3
        self.assertEqual(first,     1.4*base)
        self.assertEqual(second,    3*base)
        self.assertEqual(next(gen), 5*base)
        self.assertEqual(next(gen), 7*base)
        self.assertEqual(next(gen), 9*base)

    def test_imperiali(self):
        gen = imperiali_gen()
        first = next(gen)
        base = first/2
        self.assertEqual(first,     2*base)
        self.assertEqual(next(gen), 3*base)
        self.assertEqual(next(gen), 4*base)
        self.assertEqual(next(gen), 5*base)
        self.assertEqual(next(gen), 6*base)

    def test_danish(self):
        gen = danish_gen()
        first = next(gen)
        base = first/0.33
        self.assertEqual(first,     0.33*base)
        self.assertEqual(next(gen), 1.33*base)
        self.assertEqual(next(gen), 2.33*base)
        self.assertEqual(next(gen), 3.33*base)
        self.assertEqual(next(gen), 4.33*base)

    def test_huntington_hill(self):
        gen = huntington_hill_gen()
        first = next(gen)
        second = next(gen)
        base = second/math.sqrt(2)
        self.assertEqual(second,    math.sqrt(1*2)*base)
        self.assertEqual(next(gen), math.sqrt(2*3)*base)
        self.assertEqual(next(gen), math.sqrt(3*4)*base)
        self.assertEqual(next(gen), math.sqrt(4*5)*base)
        for i in range(1000):
            self.assertGreater(1/first, 1/next(gen))

class TestApportionment1d(unittest.TestCase):

    def test_apportionment_dhondt(self):
        votes = [301.0, 200.0]
        num_seats = 5
        prior_allocations = [1, 1]
        res = apportion1d(votes, num_seats, prior_allocations, dhondt_gen)
        self.assertEqual(res[0], [3, 2])

    def test_apportionment_sainte_lague(self):
        votes = [501.0, 400.0]
        num_seats = 5
        prior_allocations = [1, 1]
        res = apportion1d(votes, num_seats, prior_allocations, sainte_lague_gen)
        self.assertEqual(res[0], [3, 2])
