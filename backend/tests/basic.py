import unittest

from voting import ElectionRules, Election
from rules import Rules

class TestRules(unittest.TestCase):
    def test_fail_assign_with_value_rule(self):
        r = Rules()
        r.value_rules["a"] = [1]
        with self.assertRaises(ValueError):
            r["a"] = 2

    def test_succeed_assign_with_value_rule(self):
        r = Rules()
        r.value_rules["a"] = [1]
        r["a"] = 1

    def test_fail_assign_with_range_rule(self):
        r = Rules()
        r.range_rules["a"] = [1,3]
        with self.assertRaises(ValueError):
            r["a"] = 4

    def test_succeed_assign_with_range_rule(self):
        r = Rules()
        r.range_rules["a"] = [1,3]
        r["a"] = 2

    def test_fail_assign_with_list_rule(self):
        r = Rules()
        r.list_rules.append("a")
        with self.assertRaises(ValueError):
            r["a"] = 4

    def test_succeed_assign_with_list_rule(self):
        r = Rules()
        r.list_rules.append("a")
        r["a"] = ["yay"]


class TestBasicAllocation(unittest.TestCase):
    def test_election_basic(self):
        rules = ElectionRules()
        rules["constituencies"] = [
            {"name": "I",  "num_const_seats": 1, "num_adj_seats": 2},
            {"name": "II", "num_const_seats": 2, "num_adj_seats": 1}
        ]
        rules["parties"] = ["A", "B"]

        votes = [[501, 400], [301, 200]]
        election = Election(rules, votes)
        election.run()
        self.assertEqual(election.results, [[2, 1], [2, 1]])

    def test_election_basic2(self):
        rules = ElectionRules()
        rules["constituencies"] = [
            {"name": "I",  "num_const_seats": 1, "num_adj_seats": 1},
            {"name": "II", "num_const_seats": 1, "num_adj_seats": 1}
        ]
        rules["parties"] = ["A", "B", "C"]
        rules["divisor"] = "dhondt"
        rules["adjustment_threshold"] = 0.0
        votes = [[4000, 2000, 3500], [3000, 1000, 2500]]

        election = Election(rules, votes)
        election.run()
        self.assertEqual(election.results, [[1, 1, 0], [1, 0, 1]])
