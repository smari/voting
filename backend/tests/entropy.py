import unittest

from division_rules import dhondt_gen, sainte_lague_gen
from electionRules import ElectionRules
from voting import Election
from table_util import entropy

class TestEntropy(unittest.TestCase):
    def setUp(self):
        self.rules = ElectionRules()
        self.rules["debug"] = True
        self.rules["show_entropy"] = True
        self.rules["parties"] = ["A", "B"]
        self.rules["adjustment_method"] = "alternating-scaling"
        self.rules["constituencies"] = [
            {"name": "I",  "num_const_seats": 2, "num_adj_seats": 1},
            {"name": "II", "num_const_seats": 3, "num_adj_seats": 2}
        ]
        self.votes = [[500, 400],[300, 200]]
        self.election = Election(self.rules, self.votes)
        self.election.run()

    def test_entropy_calculation(self):
        self.assertEqual(round(self.election.entropy(), 2), 42.95)

    def test_entropy_depenency_on_divisor(self):
        dd_entropy = self.election.entropy()
        ds_entropy = entropy(self.votes, self.election.results, sainte_lague_gen)
        self.rules["primary_divider"] = "sainte-lague"
        self.rules["adj_determine_divider"] = "sainte-lague"
        self.rules["adj_alloc_divider"] = "sainte-lague"
        self.sl_election = Election(self.rules, self.votes)
        self.sl_election.run()
        ss_entropy = self.sl_election.entropy()
        sd_entropy = entropy(self.votes, self.sl_election.results, dhondt_gen)
        self.assertNotEqual(ds_entropy, dd_entropy)
        self.assertNotEqual(ss_entropy, dd_entropy)
        self.assertNotEqual(ss_entropy, sd_entropy)
        self.assertNotEqual(ds_entropy, sd_entropy)
        self.assertEqual(round(dd_entropy, 2), 42.95)
        self.assertEqual(round(ds_entropy, 2), 46.77)
        self.assertEqual(round(ss_entropy, 2), 46.77)
        self.assertEqual(round(sd_entropy, 2), 42.95)
