import math
import unittest

from voting import apportion1d
from division_rules import dhondt_gen, sainte_lague_gen, \
    nordic_sainte_lague_gen, imperiali_gen, danish_gen, huntington_hill_gen

class TestDivisors(unittest.TestCase):

    def test_dhondt(self):
        gen = dhondt_gen()
        self.assertEqual(next(gen), 1)
        self.assertEqual(next(gen), 2)
        self.assertEqual(next(gen), 3)
        self.assertEqual(next(gen), 4)
        self.assertEqual(next(gen), 5)

    def test_lague(self):
        gen = sainte_lague_gen()
        self.assertEqual(next(gen), 1)
        self.assertEqual(next(gen), 3)
        self.assertEqual(next(gen), 5)
        self.assertEqual(next(gen), 7)
        self.assertEqual(next(gen), 9)

    def test_nordic_lague(self):
        gen = nordic_sainte_lague_gen()
        self.assertEqual(next(gen), 1.4)
        self.assertEqual(next(gen), 3)
        self.assertEqual(next(gen), 5)
        self.assertEqual(next(gen), 7)
        self.assertEqual(next(gen), 9)

    def test_imperiali(self):
        gen = imperiali_gen()
        self.assertEqual(next(gen), 1)
        self.assertEqual(next(gen), 1.5)
        self.assertEqual(next(gen), 2)
        self.assertEqual(next(gen), 2.5)
        self.assertEqual(next(gen), 3)

    def test_danish(self):
        gen = danish_gen()
        self.assertEqual(next(gen), 0.33)
        self.assertEqual(next(gen), 1.33)
        self.assertEqual(next(gen), 2.33)
        self.assertEqual(next(gen), 3.33)
        self.assertEqual(next(gen), 4.33)

    def test_huntington_hill(self):
        gen = huntington_hill_gen()
        self.assertEqual(next(gen), 10000000000)
        self.assertEqual(next(gen), math.sqrt(2))
        self.assertEqual(next(gen), math.sqrt(6))
        self.assertEqual(next(gen), math.sqrt(12))
        self.assertEqual(next(gen), math.sqrt(20))

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
