import unittest

from voting import ElectionRules, Election
from util import add_totals

class TestElection(unittest.TestCase):

    def test_get_results(self):
        rules = ElectionRules()
        rules["parties"] = ["A", "B"]
        rules["adjustment_method"] = "alternating-scaling"
        rules["constituency_names"] = ["I", "II"]
        rules["constituency_seats"] = [2, 3]
        rules["constituency_adjustment_seats"] = [1, 2]
        votes = [[500, 400],[300, 200]]
        election = Election(rules, votes)
        election.run()
        res = election.get_results_dict()
        print(res)
        self.assertEqual(res["rules"], rules)
        self.assertEqual(res["seat_allocations"], add_totals([[2, 1], [3, 2]]))
