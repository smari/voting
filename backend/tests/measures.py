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
        self.vote_table = {
            "name": "Measure test",
            "parties": ["A", "B"],
            "votes":  [[500, 600],
                       [200, 400],
                       [350, 450]],
            "constituencies": [
                {"name": "I",   "num_const_seats": 1, "num_adj_seats": 0},
                {"name": "II",  "num_const_seats": 1, "num_adj_seats": 0},
                {"name": "III", "num_const_seats": 1, "num_adj_seats": 0},
            ],
        }
        self.votes = self.vote_table["votes"]
        self.e_rules["parties"] = self.vote_table["parties"]
        self.e_rules["constituencies"] = self.vote_table["constituencies"]
        self.e_rules["adjustment_method"] = "icelandic-law"
        election = voting.Election(self.e_rules, self.votes)
        comparison_rules = self.e_rules.generate_all_adj_ruleset()
        comparison_election = voting.Election(comparison_rules, self.votes)
        sim = simulate.Simulation(self.s_rules, [self.e_rules], self.vote_table)

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

    def test_adj_dev_with_no_deviation(self):
        #Arrange
        self.vote_table = {
            "name": "Measure test",
            "parties": [ "A",  "B"],
            "votes":  [[1500, 1000],
                       [1000, 5000]],
            "constituencies": [
                {"name": "I",  "num_const_seats": 1, "num_adj_seats": 1},
                {"name": "II", "num_const_seats": 1, "num_adj_seats": 1},
            ],
        }
        self.votes = self.vote_table["votes"]
        self.e_rules["parties"] = self.vote_table["parties"]
        self.e_rules["constituencies"] = self.vote_table["constituencies"]
        self.e_rules["adjustment_method"] = "icelandic-law"
        election = voting.Election(self.e_rules, self.votes)
        comparison_rules = self.e_rules.generate_one_const_ruleset()
        v_votes = [sum(x) for x in zip(*self.votes)]
        comparison_election = voting.Election(comparison_rules, [v_votes])
        sim = simulate.Simulation(self.s_rules, [self.e_rules], self.vote_table)

        #Act
        base_results = election.run()
        comparison_results = comparison_election.run()
        sim.simulate()
        sim_result = sim.get_results_dict()

        #Assert
        list_measures = sim_result['data'][0]['list_measures']
        self.assertEqual(list_measures["total_seats"]['avg'],
                         add_totals(base_results))

        self.assertEqual(base_results,       [[1, 1],
                                              [0, 2]])
        base_totals = [sum(x) for x in zip(*base_results)]
        self.assertEqual(base_totals,         [1, 3])
        self.assertEqual(comparison_results, [[1, 3]])
        deviation = simulate.dev([base_totals], comparison_results)
        self.assertEqual(deviation, 0)

        self.assertEqual(deviation, election.adj_dev)

        measures = sim_result['data'][0]['measures']
        self.assertEqual(measures['adj_dev']['avg'], deviation)

    def test_adj_dev_with_deviation(self):
        #Arrange
        self.vote_table = {
            "name": "Measure test",
            "parties": [ "A",  "B"],
            "votes":  [[1500,    0],
                       [   0, 5000]],
            "constituencies": [
                {"name": "I",  "num_const_seats": 1, "num_adj_seats": 1},
                {"name": "II", "num_const_seats": 1, "num_adj_seats": 1},
            ],
        }
        self.votes = self.vote_table["votes"]
        self.e_rules["parties"] = self.vote_table["parties"]
        self.e_rules["constituencies"] = self.vote_table["constituencies"]
        self.e_rules["adjustment_method"] = "icelandic-law"
        election = voting.Election(self.e_rules, self.votes)
        comparison_rules = self.e_rules.generate_one_const_ruleset()
        v_votes = [sum(x) for x in zip(*self.votes)]
        comparison_election = voting.Election(comparison_rules, [v_votes])

        #Act
        base_results = election.run()
        comparison_results = comparison_election.run()

        #Assert
        self.assertEqual(base_results,       [[2, 0],
                                              [0, 2]])
        base_totals = [sum(x) for x in zip(*base_results)]
        self.assertEqual(base_totals,         [2, 2])
        self.assertEqual(comparison_results, [[1, 3]])
        deviation = simulate.dev([base_totals], comparison_results)
        self.assertEqual(deviation, 2)

        self.assertEqual(deviation, election.adj_dev)
