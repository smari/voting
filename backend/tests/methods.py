from unittest import TestCase

import logging
import voting
import util


class MethodsTestMeta(type):
    def __new__(cls, name, bases, attrs):
        for method in voting.ADJUSTMENT_METHODS.keys():
            attrs['test_%s' % method] = cls.gen(method)

        return super(MethodsTestMeta, cls).__new__(cls, name, bases, attrs)

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


class MethodsTest(TestCase):
    __metaclass__ = MethodsTestMeta
