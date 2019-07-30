from unittest import TestCase

import logging
import util
import division_rules
from electionRules import ElectionRules
from voting import Election

from methods.alternating_scaling import *
from methods.norwegian_law import norwegian_apportionment
from methods.norwegian_icelandic import norw_ice_apportionment
from methods.pure_vote_ratios import pure_vote_ratios_apportionment


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
        row_sums = [10,
                    1]
        col_sums =  [  1,    1,    5,   1,   1,   0,    2,   0]
        votes    = [[926, 1098, 3900, 906, 878, 754, 2331, 776],
                    [926, 1098, 3900, 906, 878, 754, 2331, 776]]
        priors   = [[  1,    1,    4,   1,   1,   0,    2,   0],
                    [  0,    0,    0,   0,   0,   0,    0,   0]]
        expected = [[  1,    1,    4,   1,   1,   0,    2,   0],
                    [  0,    0,    1,   0,   0,   0,    0,   0]]

        #Act
        results, _ = alternating_scaling(
            m_votes=votes,
            v_desired_row_sums=row_sums,
            v_desired_col_sums=col_sums,
            m_prior_allocations=priors,
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
    def test_relative_superiority_simple(self):
        self.rules["adjustment_method"] = "relative-superiority-simple"
        election = Election(self.rules, self.votes)
        results = election.run()
        self.assertEqual(results, [[0,4,2,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,4,2,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [0,4,4,0,0,0,0,0,0,0,0,2,0,0,0],
                                   [1,3,5,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,2,3,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,2,3,0,0,0,0,0,0,0,0,1,0,2,1]])
        steps_table = election.demonstration_table
        steps = steps_table["steps"]
        self.assertEqual(9, len(steps))
        self.assertEqual(1.228, steps[0][4])
        self.assertEqual(1.385, steps[1][4])
        self.assertEqual(1.227, steps[2][4])
        self.assertEqual(1.15,  steps[3][4])
        self.assertEqual(1.135, steps[4][4])
        self.assertEqual(1.084, steps[5][4])
        self.assertEqual(1.078, steps[6][4])
        self.assertEqual("N/A", steps[7][4])
        self.assertEqual("N/A", steps[8][4])
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
        steps_table = election.demonstration_table
        steps = steps_table["steps"]
        self.assertEqual(9, len(steps))
        self.assertEqual(1.332, steps[0][4])
        self.assertEqual(1.385, steps[1][4])
        self.assertEqual(1.397, steps[2][4])
        self.assertEqual(2.147, steps[3][4])
        self.assertEqual(1.725, steps[4][4])
        self.assertEqual(1.739, steps[5][4])
        self.assertEqual(1.346, steps[6][4])
        self.assertEqual(1.084, steps[7][4])
        self.assertEqual("N/A", steps[8][4])
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
        self.assertEqual(results, [[0,3,3,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,4,2,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [1,4,3,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,3,5,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [2,2,3,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_norwegian_law_6c(self):
        self.rules_6c["adjustment_method"] = "norwegian-law"
        self.rules_6c["primary_divider"] = "nordic"
        self.rules_6c["adj_determine_divider"] = "dhondt"
        self.rules_6c["adj_alloc_divider"] = "sainte-lague"
        election = Election(self.rules_6c, self.votes)
        results = election.run()
        self.assertEqual(results, [[0,4,2,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [1,4,2,0,0,0,0,0,0,0,0,1,0,2,0],
                                   [1,4,3,0,0,0,0,0,0,0,0,1,0,1,0],
                                   [2,2,5,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,4,0,0,0,0,0,0,0,0,2,0,1,1],
                                   [1,2,3,0,0,0,0,0,0,0,0,2,0,2,1]])
    def test_norwegian_law_small(self):
        #Arrange
        constituencies = [
            {"name": "I",  "num_const_seats": 0, "num_adj_seats": 1},
            {"name": "II", "num_const_seats": 1, "num_adj_seats": 0},
        ]
        row_sums =        [1,
                           1]
        col_sums =  [0, 2]
        votes    = [[1, 1],
                    [1, 4]]
        priors   = [[0, 0],
                    [0, 1]]
        expected = [[0, 1],
                    [0, 1]]

        #Act
        results, _ = norwegian_apportionment(
            m_votes=votes,
            orig_votes=votes,
            v_const_seats=[con["num_const_seats"] for con in constituencies],
            v_desired_row_sums=row_sums,
            v_desired_col_sums=col_sums,
            m_prior_allocations=priors,
            divisor_gen=division_rules.dhondt_gen,
            threshold=5
        )

        #Assert
        self.assertEqual(expected, results)

    def test_norw_ice_small(self):
        #Arrange
        row_sums =        [1,
                           1]
        col_sums =  [0, 2]
        votes    = [[1, 1],
                    [1, 4]]
        priors   = [[0, 0],
                    [0, 1]]
        expected = [[0, 1],
                    [0, 1]]

        #Act
        results, _ = norw_ice_apportionment(
            m_votes=votes,
            orig_votes=votes,
            v_desired_row_sums=row_sums,
            v_desired_col_sums=col_sums,
            m_prior_allocations=priors,
            divisor_gen=division_rules.dhondt_gen,
            threshold=5
        )

        #Assert
        self.assertEqual(expected, results)

    def test_pure_votes_small(self):
        #Arrange
        row_sums =        [1,
                           1]
        col_sums =  [0, 2]
        votes    = [[1, 1],
                    [1, 4]]
        priors   = [[0, 0],
                    [0, 1]]
        expected = [[0, 1],
                    [0, 1]]

        #Act
        results, _ = pure_vote_ratios_apportionment(
            m_votes=votes,
            orig_votes=votes,
            v_desired_row_sums=row_sums,
            v_desired_col_sums=col_sums,
            m_prior_allocations=priors,
            divisor_gen=division_rules.dhondt_gen,
            threshold=5
        )

        #Assert
        self.assertEqual(expected, results)


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
