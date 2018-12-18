import unittest

from voting import dhondt_gen, sainte_lague_gen
from voting import ElectionRules, Election
from rules import Rules
from util import add_totals, entropy

class TestEntropy(unittest.TestCase):
    def setUp(self):
        self.rules = ElectionRules()
        self.rules["debug"] = True
        self.rules["show_entropy"] = True
        self.rules["parties"] = ["A", "B"]
        self.rules["adjustment_method"] = "alternating-scaling"
        self.rules["constituency_names"] = ["I", "II"]
        self.rules["constituency_seats"] = [2, 3]
        self.rules["constituency_adjustment_seats"] = [1, 2]
        self.votes = [[500, 400],[300, 200]]
        self.election = Election(self.rules, self.votes)
        self.election.run()

    def test_entropy_calculation(self):
        self.assertEqual(round(self.election.entropy(), 2), 42.95)

    def test_entropy_depenency_on_divisor(self):
        dd_entropy = self.election.entropy()
        ds_entropy = entropy(self.votes, self.election.results, sainte_lague_gen)
        self.assertNotEqual(ds_entropy, dd_entropy)
        self.assertEqual(round(ds_entropy, 2), 41.22)
        self.assertEqual(round(dd_entropy, 2), 42.95)
