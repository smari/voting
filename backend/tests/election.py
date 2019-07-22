import unittest

from voting import ElectionRules, Election
from table_util import add_totals

class TestElection(unittest.TestCase):

    def test_get_results(self):
        rules = ElectionRules()
        rules["parties"] = ["A", "B"]
        rules["adjustment_method"] = "alternating-scaling"
        rules["constituencies"] = [
            {"name": "I",  "num_const_seats": 2, "num_adj_seats": 1},
            {"name": "II", "num_const_seats": 3, "num_adj_seats": 2}
        ]
        votes = [[500, 400],[300, 200]]
        election = Election(rules, votes)
        election.run()
        res = election.get_results_dict()
        print(res)
        self.assertEqual(res["rules"], rules)
        self.assertEqual(res["seat_allocations"], add_totals([[2, 1], [3, 2]]))

    def test_invalid(self):
        rules = ElectionRules()
        rules["parties"] = ["A", "B"]
        rules["adjustment_method"] = "icelandic-law"
        rules["adjustment_threshold"] = 5
        rules["constituencies"] = [
            {"name": "I",  "num_const_seats": 0, "num_adj_seats": 1},
            {"name": "II", "num_const_seats": 0, "num_adj_seats": 1}
        ]
        votes = [[1, 0],[0, 100]]
        election = Election(rules, votes)
        with self.assertRaises(ValueError):
            election.run()
