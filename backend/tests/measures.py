# coding:utf-8
from unittest import TestCase
from random import uniform

import logging
import simulate
import voting
from table_util import add_totals


class MeasureTest(TestCase):
    def setUp(self):
        self.e_rules = voting.ElectionRules()
        self.s_rules = simulate.SimulationRules()
        self.s_rules["simulation_count"] = 0

    def test_all_adj(self):
        #Arrange
        self.e_rules["adjustment_method"] = "icelandic-law"
        self.e_rules["constituency_names"]            = ["I", "II", "III"]
        self.e_rules["constituency_seats"]            = [ 1,    1,     1 ]
        self.e_rules["constituency_adjustment_seats"] = [ 0,    0,     0 ]
        self.e_rules["parties"] = ["A", "B"]
        self.votes =             [[500, 600],
                                  [200, 400],
                                  [350, 450]]
        election = voting.Election(self.e_rules, self.votes)
        comparison_rules = self.e_rules.generate_all_adj_ruleset()
        comparison_election = voting.Election(comparison_rules, self.votes)
        sim = simulate.Simulation(self.s_rules, [self.e_rules], self.votes, '')

        #Act
        base_results = election.run()
        comparison_results = comparison_election.run()
        sim.simulate()
        sim_result = sim.get_results_dict()

        #Assert
        list_measures = sim_result['data'][0]['list_measures']
        self.assertEqual(list_measures["total_seats"]['avg'],
                         add_totals(base_results))

        self.assertEqual(base_results,       [[0, 1],
                                              [0, 1],
                                              [0, 1]])
        self.assertEqual(comparison_results, [[1, 0],
                                              [0, 1],
                                              [0, 1]])
        deviation = simulate.dev(base_results, comparison_results)
        self.assertEqual(deviation, 2)

        measures = sim_result['data'][0]['measures']
        self.assertEqual(measures['dev_all_adj']['avg'], deviation)

    def test_adj_dev(self):
        #Arrange
        self.e_rules["adjustment_method"] = "icelandic-law"
        self.e_rules["constituency_names"]            = ["I", "II"]
        self.e_rules["constituency_seats"]            = [ 1,    1 ]
        self.e_rules["constituency_adjustment_seats"] = [ 1,    1 ]
        self.e_rules["parties"] = ["A", "B"]
        self.votes =             [[1500, 0],
                                  [0, 5000]]
        election = voting.Election(self.e_rules, self.votes)
        comparison_rules = self.e_rules.generate_one_const_ruleset()
        v_votes = [sum(x) for x in zip(*self.votes)]
        comparison_election = voting.Election(comparison_rules, [v_votes])
        sim = simulate.Simulation(self.s_rules, [self.e_rules], self.votes, '')

        #Act
        base_results = election.run()
        comparison_results = comparison_election.run()
        sim.simulate()
        sim_result = sim.get_results_dict()

        #Assert
        list_measures = sim_result['data'][0]['list_measures']
        self.assertEqual(list_measures["total_seats"]['avg'],
                         add_totals(base_results))

        self.assertEqual(base_results,       [[2, 0],
                                              [0, 2]])
        base_totals = [sum(x) for x in zip(*base_results)]
        self.assertEqual(base_totals,         [2, 2])
        self.assertEqual(comparison_results, [[1, 3]])
        deviation = simulate.dev([base_totals], comparison_results)
        self.assertEqual(deviation, 2)

        measures = sim_result['data'][0]['measures']
        self.assertEqual(measures['adj_dev']['avg'], deviation)
