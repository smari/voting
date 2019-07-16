from unittest import TestCase

import logging
import util
import division_rules
from electionRules import ElectionRules
from voting import Election

from methods.alternating_scaling import *


class AdjustmentMethodsTestMeta(type):
    def __new__(cls, name, bases, attrs):
        for method in voting.ADJUSTMENT_METHODS.keys():
            attrs['test_%s' % method] = cls.gen(method)

        return super(AdjustmentMethodsTestMeta, cls).__new__(cls, name, bases, attrs)

    @classmethod
    def gen(cls, method):
        def fn(self):
            rules = ElectionRules()

            votes_file = "../data/elections/iceland_2013_landskjorstjorn.csv"
            const_file = "../data/constituencies/constituencies_iceland_2013.csv"
            rules["constituencies"] = const_file
            parties, votes = util.load_votes(votes_file, rules["constituencies"])
            rules["parties"] = parties

            rules["adjustment_method"] = method
            election = Election(rules, votes)
            election.run()

        return fn


class AdjustmentMethodsTest(TestCase):
    __metaclass__ = AdjustmentMethodsTestMeta

class TestAdjustmentMethods(TestCase):
    def setUp(self):
        self.rules = ElectionRules()
        self.rules_6c = ElectionRules()
        votes_file = "../data/elections/iceland_2013_landskjorstjorn.csv"
        const_file = "../data/constituencies/constituencies_iceland_2013.csv"
        const_file_6c = "../data/constituencies/iceland_2013_6x6.xlsx"
        self.rules["constituencies"] = const_file
        self.rules_6c["constituencies"] = const_file_6c
        parties, votes = util.load_votes(votes_file, self.rules["constituencies"])
        self.rules["parties"] = parties
        self.rules_6c["parties"] = parties
        self.rules["adjustment_threshold"] = 5
        self.rules_6c["adjustment_threshold"] = 5
        self.votes = votes

    def test_alternating_scaling_small(self):
        with self.assertRaises(ValueError):
            results, _ = alternating_scaling(
                m_votes=[[1500,    0],
                         [   0, 5000]],
                v_desired_row_sums=        [2,
                                            2],
                v_desired_col_sums=  [1,3],
                m_prior_allocations=[[1,0],
                                     [0,1]],
                divisor_gen=division_rules.dhondt_gen,
                threshold=5
            )

    def test_alternating_scaling_diverging(self):
        with self.assertRaises(ValueError):
            results, _ = alternating_scaling(
                m_votes=[[1500,    0],
                         [   0, 5000]],
                v_desired_row_sums=        [2,
                                            2],
                v_desired_col_sums=  [1,3],
                m_prior_allocations=[[1,0],
                                     [0,2]],
                divisor_gen=division_rules.dhondt_gen,
                threshold=5
            )

    def test_alternating_scaling_hafnarfj(self):
        #Arrange
        col_sums = [10,
                    1]
        row_sums =  [  1,    1,    5,   1,   1,   0,    2,   0]
        votes    = [[926, 1098, 3900, 906, 878, 754, 2331, 776],
                    [926, 1098, 3900, 906, 878, 754, 2331, 776]]
        priors   = [[  1,    1,    4,   1,   1,   0,    2,   0],
                    [  0,    0,    0,   0,   0,   0,    0,   0]]
        expected = [[  1,    1,    4,   1,   1,   0,    2,   0],
                    [  0,    0,    1,   0,   0,   0,    0,   0]]

        #Act
        results, _ = alternating_scaling(
            m_votes=votes,
            m_prior_allocations=priors,
            v_desired_col_sums=row_sums,
            v_desired_row_sums=col_sums,
            divisor_gen=division_rules.dhondt_gen,
            threshold=5
        )

        #Assert
        self.assertEqual(expected, results)

    def test_alternating_scaling(self):
        self.rules["adjustment_method"] = "alternating-scaling"
        election = Election(self.rules, self.votes)
        results = election.run()
        self.assertEqual(results, [[0,4,2,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,4,2,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [1,4,4,0,0,0,0,0,0,0,0,1,0,0,0],
                                   [1,3,5,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,2,3,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_alternating_scaling_lague(self):
        self.rules["primary_divider"] = "sainte-lague"
        self.rules["adj_determine_divider"] = "sainte-lague"
        self.rules["adj_alloc_divider"] = "sainte-lague"
        self.rules["adjustment_method"] = "alternating-scaling"
        election = Election(self.rules, self.votes)
        results = election.run()
        self.assertEqual(results, [[1,3,2,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,3,3,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [0,4,3,0,0,0,0,0,0,0,0,1,0,1,1],
                                   [1,3,5,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,2,3,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_alternating_scaling_6c(self):
        self.rules_6c["adjustment_method"] = "alternating-scaling"
        election = Election(self.rules_6c, self.votes)
        results = election.run()
        self.assertEqual(results, [[0,3,3,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,4,2,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [0,4,4,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [2,3,4,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,2,3,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_var_alt_scal(self):
        self.rules["adjustment_method"] = "var-alt-scal"
        election = Election(self.rules, self.votes)
        results = election.run()
        self.assertEqual(results, [[0,4,2,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,4,2,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [1,4,4,0,0,0,0,0,0,0,0,1,0,0,0],
                                   [1,3,5,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,2,3,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_var_alt_scal_6c(self):
        self.rules_6c["adjustment_method"] = "var-alt-scal"
        election = Election(self.rules_6c, self.votes)
        results = election.run()
        self.assertEqual(results, [[0,3,3,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,4,2,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [0,4,4,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [2,3,4,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,2,3,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_icelandic_law(self):
        self.rules["adjustment_method"] = "icelandic-law"
        election = Election(self.rules, self.votes)
        results = election.run()
        self.assertEqual(results, [[0,4,2,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,4,2,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [1,4,4,0,0,0,0,0,0,0,0,1,0,0,0],
                                   [1,3,5,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,2,3,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_icelandic_law_6c(self):
        self.rules_6c["adjustment_method"] = "icelandic-law"
        election = Election(self.rules_6c, self.votes)
        results = election.run()
        self.assertEqual(results, [[0,4,2,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,4,2,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [0,4,4,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,3,5,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,2,3,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,1,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_switching(self):
        self.rules["adjustment_method"] = "switching"
        election = Election(self.rules, self.votes)
        results = election.run()
        self.assertEqual(results, [[0,4,2,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,4,2,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [1,4,4,0,0,0,0,0,0,0,0,1,0,0,0],
                                   [1,3,5,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,2,3,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_switching_6c(self):
        self.rules_6c["adjustment_method"] = "switching"
        election = Election(self.rules_6c, self.votes)
        results = election.run()
        self.assertEqual(results, [[0,4,2,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,4,2,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [1,4,4,0,0,0,0,0,0,0,0,1,0,0,0],
                                   [2,2,5,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_monge(self):
        self.rules["adjustment_method"] = "monge"
        election = Election(self.rules, self.votes)
        results = election.run()
        self.assertEqual(0, 0)
    def test_nearest_neighbor(self):
        self.rules["adjustment_method"] = "nearest-neighbor"
        election = Election(self.rules, self.votes)
        results = election.run()
        self.assertEqual(results, [[0,4,2,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [0,4,3,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [1,4,4,0,0,0,0,0,0,0,0,1,0,0,0],
                                   [2,3,4,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,2,3,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_nearest_neighbor_6c(self):
        self.rules_6c["adjustment_method"] = "nearest-neighbor"
        election = Election(self.rules_6c, self.votes)
        results = election.run()
        self.assertEqual(results, [[1,3,2,0,0,0,0,0,0,0,0,1,0,0,1],
                                   [1,3,2,0,0,0,0,0,0,0,0,1,0,3,0],
                                   [0,5,4,0,0,0,0,0,0,0,0,1,0,0,0],
                                   [1,4,5,0,0,0,0,0,0,0,0,2,0,1,0],
                                   [1,2,4,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,1,2,0,0,0,0,0,0,0,0,2,0,3,1]])
    def test_norwegian_icelandic(self):
        self.rules["adjustment_method"] = "norwegian-icelandic"
        election = Election(self.rules, self.votes)
        results = election.run()
        self.assertEqual(results, [[0,4,2,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,4,2,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [1,4,4,0,0,0,0,0,0,0,0,1,0,0,0],
                                   [1,3,5,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,2,3,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_norwegian_icelandic_6c(self):
        self.rules_6c["adjustment_method"] = "norwegian-icelandic"
        election = Election(self.rules_6c, self.votes)
        results = election.run()
        self.assertEqual(results, [[1,3,2,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [0,4,3,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [2,4,3,0,0,0,0,0,0,0,0,1,0,0,0],
                                   [1,3,5,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_relative_superiority(self):
        self.rules["adjustment_method"] = "relative-superiority"
        election = Election(self.rules, self.votes)
        results = election.run()
        self.assertEqual(results, [[0,4,2,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,4,2,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [1,4,4,0,0,0,0,0,0,0,0,1,0,0,0],
                                   [1,3,5,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,2,3,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_relative_superiority_6c(self):
        self.rules_6c["adjustment_method"] = "relative-superiority"
        election = Election(self.rules_6c, self.votes)
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
        election = Election(self.rules, self.votes)
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
        election = Election(self.rules_6c, self.votes)
        results = election.run()
        self.assertEqual(results, [[1,3,2,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,4,2,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [1,4,3,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,3,5,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,4,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])

class DividerRulesTestMeta(type):
    def __new__(cls, name, bases, attrs):
        for rule in division_rules.DIVIDER_RULES.keys():
            attrs['test_%s' % rule] = cls.gen(rule)

        return super(DividerRulesTestMeta, cls).__new__(cls, name, bases, attrs)

    @classmethod
    def gen(cls, rule):
        def fn(self):
            self.rules["primary_divider"] = rule
            self.rules["adjustment_divider"] = rule
            election = Election(self.rules, self.votes)
            election.run()

        return fn


class DividerRulesTest(TestCase):
    __metaclass__ = DividerRulesTestMeta

    def setUp(self):
        self.rules = ElectionRules()
        votes_file = "../data/elections/iceland_2013_landskjorstjorn.csv"
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
