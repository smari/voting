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
