# coding:utf-8
from unittest import TestCase
from random import uniform

import logging
import simulate
import voting
import util


class MeasureTest(TestCase):
    def setUp(self):
        self.e_rules = voting.ElectionRules()
        self.e_rules["constituency_names"]            = ["I", "II", "III"]
        self.e_rules["constituency_seats"]            = [ 1,    1,     1 ]
        self.e_rules["constituency_adjustment_seats"] = [ 0,    0,     0 ]
        self.e_rules["parties"] = ["A", "B"]
        self.votes =             [[500, 600],
                                  [200, 400],
                                  [350, 450]]
        self.s_rules = simulate.SimulationRules()
        self.s_rules["simulation_count"] = 0

    def test_all_adj(self):
        #Arrange
        election = voting.Election(self.e_rules, self.votes)
        comparison_rules = simulate.generate_all_adj_ruleset(self.e_rules)
        comparison_election = voting.Election(comparison_rules, self.votes)
        sim = simulate.Simulation(self.s_rules, [self.e_rules], self.votes)

        #Act
        base_results = election.run()
        comparison_results = comparison_election.run()
        sim.simulate()
        sim_result = sim.get_results_dict()

        #Assert
        list_measures = sim_result['data'][0]['list_measures']
        self.assertEqual(list_measures["total_seats"]['avg'],
                         util.add_totals(base_results))

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
        self.assertEqual(measures['dev_all_adj']['var'], 0)
        self.assertEqual(measures['dev_all_adj']['cnt'], 1)
