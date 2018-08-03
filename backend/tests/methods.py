from unittest import TestCase

import logging
import voting
import util


class AdjustmentMethodsTestMeta(type):
    def __new__(cls, name, bases, attrs):
        for method in voting.ADJUSTMENT_METHODS.keys():
            attrs['test_%s' % method] = cls.gen(method)

        return super(AdjustmentMethodsTestMeta, cls).__new__(cls, name, bases, attrs)

    @classmethod
    def gen(cls, method):
        def fn(self):
            rules = voting.ElectionRules()

            votes_file = "../data/elections/iceland_landskjorstjorn_2013.csv"
            const_file = "../data/constituencies/constituencies_iceland_2013.csv"
            rules["constituencies"] = const_file
            parties, votes = util.load_votes(votes_file, rules["constituencies"])
            rules["parties"] = parties

            rules["adjustment_method"] = method
            election = voting.Election(rules, votes)
            election.run()

        return fn


class AdjustmentMethodsTest(TestCase):
    __metaclass__ = AdjustmentMethodsTestMeta

class TestAdjustmentMethods(TestCase):
    def setUp(self):
        self.rules = voting.ElectionRules()
        self.rules_6c = voting.ElectionRules()
        votes_file = "../data/elections/iceland_landskjorstjorn_2013.csv"
        const_file = "../data/constituencies/constituencies_iceland_2013.csv"
        const_file_6c = "../data/constituencies/iceland_2013_6x6.xlsx"
        self.rules["constituencies"] = const_file
        self.rules_6c["constituencies"] = const_file_6c
        parties, votes = util.load_votes(votes_file, self.rules["constituencies"])
        self.rules["parties"] = parties
        self.rules_6c["parties"] = parties
        self.votes = votes

    def test_alternating_scaling(self):
        self.rules["adjustment_method"] = "alternating-scaling"
        election = voting.Election(self.rules, self.votes)
        results = election.run()
        self.assertEqual(results, [[0,4,2,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,4,2,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [1,4,4,0,0,0,0,0,0,0,0,1,0,0,0],
                                   [1,3,5,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,2,3,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_alternating_scaling_6c(self):
        self.rules_6c["adjustment_method"] = "alternating-scaling"
        election = voting.Election(self.rules_6c, self.votes)
        results = election.run()
        self.assertEqual(results, [[0,3,3,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,4,2,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [0,4,4,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [2,3,4,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,2,3,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_var_alt_scal(self):
        self.rules["adjustment_method"] = "var-alt-scal"
        election = voting.Election(self.rules, self.votes)
        results = election.run()
        self.assertEqual(results, [[0,4,2,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,4,2,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [1,4,4,0,0,0,0,0,0,0,0,1,0,0,0],
                                   [1,3,5,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,2,3,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_var_alt_scal_6c(self):
        self.rules_6c["adjustment_method"] = "var-alt-scal"
        election = voting.Election(self.rules_6c, self.votes)
        results = election.run()
        self.assertEqual(results, [[0,3,3,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,4,2,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [0,4,4,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [2,3,4,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,2,3,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_icelandic_law(self):
        self.rules["adjustment_method"] = "icelandic-law"
        election = voting.Election(self.rules, self.votes)
        results = election.run()
        self.assertEqual(results, [[0,4,2,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,4,2,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [1,4,4,0,0,0,0,0,0,0,0,1,0,0,0],
                                   [1,3,5,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,2,3,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_icelandic_law_6c(self):
        self.rules_6c["adjustment_method"] = "icelandic-law"
        election = voting.Election(self.rules_6c, self.votes)
        results = election.run()
        self.assertEqual(results, [[0,4,2,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,4,2,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [0,4,4,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,3,5,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,2,3,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,1,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_switching(self):
        self.rules["adjustment_method"] = "switching"
        election = voting.Election(self.rules, self.votes)
        results = election.run()
        self.assertEqual(results, [[0,4,2,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,4,2,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [1,4,4,0,0,0,0,0,0,0,0,1,0,0,0],
                                   [1,3,5,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,2,3,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_switching_6c(self):
        self.rules_6c["adjustment_method"] = "switching"
        election = voting.Election(self.rules_6c, self.votes)
        results = election.run()
        self.assertEqual(results, [[0,4,2,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,4,2,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [1,4,4,0,0,0,0,0,0,0,0,1,0,0,0],
                                   [2,2,5,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_monge(self):
        self.rules["adjustment_method"] = "monge"
        election = voting.Election(self.rules, self.votes)
        results = election.run()
        self.assertEqual(0, 0)
    def test_nearest_neighbor(self):
        self.rules["adjustment_method"] = "nearest-neighbor"
        election = voting.Election(self.rules, self.votes)
        results = election.run()
        self.assertEqual(results, [[0,4,2,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [0,4,3,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [1,4,4,0,0,0,0,0,0,0,0,1,0,0,0],
                                   [2,3,4,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,2,3,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_nearest_neighbor_6c(self):
        self.rules_6c["adjustment_method"] = "nearest-neighbor"
        election = voting.Election(self.rules_6c, self.votes)
        results = election.run()
        self.assertEqual(results, [[1,3,2,0,0,0,0,0,0,0,0,1,0,0,1],
                                   [1,3,2,0,0,0,0,0,0,0,0,1,0,3,0],
                                   [0,5,4,0,0,0,0,0,0,0,0,1,0,0,0],
                                   [1,4,5,0,0,0,0,0,0,0,0,2,0,1,0],
                                   [1,2,4,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,1,2,0,0,0,0,0,0,0,0,2,0,3,1]])
    def test_norwegian_icelandic(self):
        self.rules["adjustment_method"] = "norwegian-icelandic"
        election = voting.Election(self.rules, self.votes)
        results = election.run()
        self.assertEqual(results, [[0,4,2,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,4,2,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [1,4,4,0,0,0,0,0,0,0,0,1,0,0,0],
                                   [1,3,5,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,2,3,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_norwegian_icelandic_6c(self):
        self.rules_6c["adjustment_method"] = "norwegian-icelandic"
        election = voting.Election(self.rules_6c, self.votes)
        results = election.run()
        self.assertEqual(results, [[1,3,2,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [0,4,3,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [2,4,3,0,0,0,0,0,0,0,0,1,0,0,0],
                                   [1,3,5,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_relative_superiority(self):
        self.rules["adjustment_method"] = "relative-superiority"
        election = voting.Election(self.rules, self.votes)
        results = election.run()
        self.assertEqual(results, [[0,4,2,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,4,2,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [1,4,4,0,0,0,0,0,0,0,0,1,0,0,0],
                                   [1,3,5,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,2,3,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_relative_superiority_6c(self):
        self.rules_6c["adjustment_method"] = "relative-superiority"
        election = voting.Election(self.rules_6c, self.votes)
        results = election.run()
        self.assertEqual(results, [[0,3,3,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,4,2,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [0,4,4,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [2,3,4,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,2,3,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_norwegian_law(self):
        self.rules["adjustment_method"] = "norwegian-law"
        self.rules["primary_divider"] = "nordic"
        self.rules["adj_determine_divider"] = "dhondt"
        self.rules["adj_alloc_divider"] = "sainte-lague"
        election = voting.Election(self.rules, self.votes)
        results = election.run()
        self.assertEqual(results, [[1,3,2,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,4,2,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [1,4,3,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,3,5,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,4,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_norwegian_law_6c(self):
        self.rules_6c["adjustment_method"] = "norwegian-law"
        self.rules_6c["primary_divider"] = "nordic"
        self.rules_6c["adj_determine_divider"] = "dhondt"
        self.rules_6c["adj_alloc_divider"] = "sainte-lague"
        election = voting.Election(self.rules_6c, self.votes)
        results = election.run()
        self.assertEqual(results, [[1,3,2,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,4,2,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [1,4,3,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,3,5,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,4,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])

class DividerRulesTestMeta(type):
    def __new__(cls, name, bases, attrs):
        for rule in voting.DIVIDER_RULES.keys():
            attrs['test_%s' % rule] = cls.gen(rule)

        return super(DividerRulesTestMeta, cls).__new__(cls, name, bases, attrs)

    @classmethod
    def gen(cls, rule):
        def fn(self):
            self.rules["primary_divider"] = rule
            self.rules["adjustment_divider"] = rule
            election = voting.Election(self.rules, self.votes)
            election.run()

        return fn


class DividerRulesTest(TestCase):
    __metaclass__ = DividerRulesTestMeta

    def setUp(self):
        self.rules = voting.ElectionRules()
        votes_file = "../data/elections/iceland_landskjorstjorn_2013.csv"
        const_file = "../data/constituencies/constituencies_iceland_2013.csv"
        self.rules["constituencies"] = const_file
        parties, votes = util.load_votes(votes_file, self.rules["constituencies"])
        self.rules["parties"] = parties
        self.rules["adjustment_method"] =  "alternating-scaling"
        self.votes = votes

    def test_nonexistant_divider_rule(self):
        self.rules["not_real"] = "fake rule that is fake"
        with self.assertRaises(ValueError):
            self.rules.get_generator("not_real")
