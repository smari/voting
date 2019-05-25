# coding:utf-8
from unittest import TestCase

from electionRules import ElectionRules

class TestElectionRules(TestCase):

    def setUp(self):
        self.rules = ElectionRules()
        self.rules["adjustment_method"] = "norwegian-law"
        self.rules["primary_divider"] = "nordic"
        self.rules["adj_determine_divider"] = "nordic"
        self.rules["adj_alloc_divider"] = "nordic"
        self.rules["adjustment_threshold"] = 4
        self.rules["parties"] = ["A", "B"]
        self.rules["constituency_names"] = ["I", "II"]
        self.rules["constituency_seats"] = [2, 3]
        self.rules["constituency_adjustment_seats"] = [1, 2]
        #self.votes = [[500, 400],[300, 200]]

    def test_generate_opt_ruleset(self):
        opt = self.rules.generate_opt_ruleset()
        self.assertEqual(opt["adjustment_method"], "alternating-scaling")
        self.assertEqual(opt["primary_divider"], "nordic")
        self.assertEqual(opt["adj_determine_divider"], "nordic")
        self.assertEqual(opt["adj_alloc_divider"], "nordic")
        self.assertEqual(opt["adjustment_threshold"], 4)
        self.assertEqual(opt["parties"], ["A", "B"])
        self.assertEqual(opt["constituency_names"], ["I", "II"])
        self.assertEqual(opt["constituency_seats"], [2, 3])
        self.assertEqual(opt["constituency_adjustment_seats"], [1, 2])

    def test_generate_law_ruleset(self):
        law = self.rules.generate_law_ruleset()
        self.assertEqual(law["adjustment_method"], "icelandic-law")
        self.assertEqual(law["primary_divider"], "dhondt")
        self.assertEqual(law["adj_determine_divider"], "dhondt")
        self.assertEqual(law["adj_alloc_divider"], "dhondt")
        self.assertEqual(law["adjustment_threshold"], 5)
        self.assertEqual(law["parties"], ["A", "B"])
        self.assertEqual(law["constituency_names"], ["I", "II"])
        self.assertEqual(law["constituency_seats"], [2, 3])
        self.assertEqual(law["constituency_adjustment_seats"], [1, 2])

    def test_generate_ind_const_ruleset(self):
        ind_const = self.rules.generate_ind_const_ruleset()
        self.assertEqual(ind_const["adjustment_method"], "norwegian-law")
        self.assertEqual(ind_const["primary_divider"], "nordic")
        self.assertEqual(ind_const["adj_determine_divider"], "nordic")
        self.assertEqual(ind_const["adj_alloc_divider"], "nordic")
        self.assertEqual(ind_const["adjustment_threshold"], 4)
        self.assertEqual(ind_const["parties"], ["A", "B"])
        self.assertEqual(ind_const["constituency_names"], ["I", "II"])
        self.assertEqual(ind_const["constituency_seats"], [3, 5])
        self.assertEqual(ind_const["constituency_adjustment_seats"], [0, 0])

    def test_generate_one_const_ruleset(self):
        one_const = self.rules.generate_one_const_ruleset()
        self.assertEqual(one_const["adjustment_method"], "norwegian-law")
        self.assertEqual(one_const["primary_divider"], "nordic")
        self.assertEqual(one_const["adj_determine_divider"], "nordic")
        self.assertEqual(one_const["adj_alloc_divider"], "nordic")
        self.assertEqual(one_const["adjustment_threshold"], 4)
        self.assertEqual(one_const["parties"], ["A", "B"])
        self.assertEqual(one_const["constituency_names"], ["All"])
        self.assertEqual(one_const["constituency_seats"], [5])
        self.assertEqual(one_const["constituency_adjustment_seats"], [3])

    def test_generate_all_adj_ruleset(self):
        all_adj = self.rules.generate_all_adj_ruleset()
        self.assertEqual(all_adj["adjustment_method"], "norwegian-law")
        self.assertEqual(all_adj["primary_divider"], "nordic")
        self.assertEqual(all_adj["adj_determine_divider"], "nordic")
        self.assertEqual(all_adj["adj_alloc_divider"], "nordic")
        self.assertEqual(all_adj["adjustment_threshold"], 4)
        self.assertEqual(all_adj["parties"], ["A", "B"])
        self.assertEqual(all_adj["constituency_names"], ["I", "II"])
        self.assertEqual(all_adj["constituency_seats"], [0, 0])
        self.assertEqual(all_adj["constituency_adjustment_seats"], [3, 5])
