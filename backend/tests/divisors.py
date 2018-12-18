import unittest

from voting import apportion1d, dhondt_gen, sainte_lague_gen

class TestDivisors(unittest.TestCase):

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
