import unittest

from voting import apportion1d, dhondt_gen, sainte_lague_gen
from voting import ElectionRules, Election

class TestMaxEntropy(unittest.TestCase):

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


class TestBasicAllocation(unittest.TestCase):
    def test_election_basic(self):
        rules = ElectionRules()
        rules["constituency_seats"] = [1, 2]
        rules["constituency_adjustment_seats"] = [2, 1]
        rules["constituency_names"] = ["I", "II"]
        rules["parties"] = ["A", "B"]

        votes = [[501, 400], [301, 200]]
        election = Election(rules, votes)
        election.run()
        self.assertEqual(election.results, [[2, 1], [2, 1]])

    def test_election_basic2(self):
        rules = ElectionRules()
        rules["constituency_seats"] = [1, 1]
        rules["constituency_adjustment_seats"] = [1, 1]
        rules["constituency_names"] = ["I", "II"]
        rules["parties"] = ["A", "B", "C"]
        rules["divisor"] = "dhondt"
        rules["adjustment_threshold"] = 0.0
        votes = [[4000, 2000, 3500], [3000, 1000, 2500]]

        election = Election(rules, votes)
        election.run()
        self.assertEqual(election.results, [[1, 1, 0], [1, 0, 1]])


if __name__ == '__main__':
    unittest.main()
