# coding:utf-8
from unittest import TestCase
from random import uniform

import logging
import simulate
from dictionaries import MEASURES, LIST_MEASURES, AGGREGATES
import voting
import util


class SimulationTest(TestCase):
    def setUp(self):
        self.vote_table = {
            "name": "Simulation test",
            "parties": ["A", "B"],
            "votes":  [[500, 300],
                       [200, 400],
                       [350, 450]],
            "constituencies": [
                {"name": "I",   "num_const_seats": 5, "num_adj_seats": 1},
                {"name": "II",  "num_const_seats": 6, "num_adj_seats": 2},
                {"name": "III", "num_const_seats": 4, "num_adj_seats": 1},
            ],
        }
        self.votes = self.vote_table["votes"]
        self.e_rules = voting.ElectionRules()
        self.s_rules = simulate.SimulationRules()
        self.s_rules["simulation_count"] = 100

    def test_generate_votes(self):
        pass
        # Generate a few vote sets

    def test_generate_votes_average(self):
        n = 1000
        self.s_rules["simulation_count"] = n
        sim = simulate.Simulation(self.s_rules, [self.e_rules], self.vote_table)
        gen = sim.gen_votes()
        r = []
        r_avg = []
        r_var = []
        for k in range(n):
            r.append([])
            generated_votes = next(gen)
            for i in range(len(self.votes)):
                r[k].append([])
                for j in range(len(self.votes[i])):
                    r[k][i].append(uniform(0.0,1.0))
        for i in range(len(self.votes)):
            r_avg.append([])
            r_var.append([])
            for j in range(len(self.votes[i])):
                r_ij = [r[k][i][j] for k in range(n)]
                # average = simulate.avg(r_ij)
                # r_avg[i].append(average)
                # r_var[i].append(simulate.var(r_ij, average))

        sim.test_generated()
        # r_avg_error = simulate.error(r_avg, 0.5)
        # r_var_error = simulate.error(r_var, 1/12.0)

        # self.assertLessEqual(r_avg_error, 0.01)


        # Verify that µ=0.5±2%

    def test_simulate_not_at_all(self):
        #Arrange
        self.s_rules["simulation_count"] = 0
        sim = simulate.Simulation(self.s_rules, [self.e_rules], self.vote_table)
        #Act
        sim.simulate()
        #Assert
        result = sim.get_results_dict()
        vote_data = result['vote_data']['sim_votes']
        list_measures = result['data'][0]['list_measures']
        for const in range(sim.num_constituencies):
            for party in range(sim.num_parties):
                self.assertEqual(
                    vote_data['sum'][const][party], self.votes[const][party]
                )
                self.assertEqual(
                    vote_data['avg'][const][party], self.votes[const][party]
                )
                self.assertEqual(
                    vote_data['max'][const][party], self.votes[const][party]
                )
                self.assertEqual(
                    vote_data['min'][const][party], self.votes[const][party]
                )
                self.assertEqual(vote_data['cnt'][const][party], 1)
                self.assertEqual(vote_data['var'][const][party], 0)
                self.assertEqual(vote_data['std'][const][party], 0)
                for m in LIST_MEASURES.keys():
                    self.assertEqual(list_measures[m]['cnt'][const][party], 1)
                    self.assertEqual(list_measures[m]['var'][const][party], 0)
                    self.assertEqual(list_measures[m]['std'][const][party], 0)
        measures = result['data'][0]['measures']
        for m in MEASURES.keys():
            self.assertEqual(measures[m]['cnt'], 1)
            self.assertEqual(measures[m]['var'], 0)
            self.assertEqual(measures[m]['std'], 0)

    def test_simulate_once(self):
        #Arrange
        self.s_rules["simulation_count"] = 1
        sim = simulate.Simulation(self.s_rules, [self.e_rules], self.vote_table)
        #Act
        sim.simulate()
        #Assert
        result = sim.get_results_dict()
        vote_data = result['vote_data']['sim_votes']
        list_measures = result['data'][0]['list_measures']
        for const in range(sim.num_constituencies):
            for party in range(sim.num_parties):
                self.assertGreater(vote_data['sum'][const][party], 0)
                self.assertGreater(vote_data['avg'][const][party], 0)
                self.assertGreater(vote_data['max'][const][party], 0)
                self.assertGreater(vote_data['min'][const][party], 0)
                self.assertEqual(vote_data['cnt'][const][party], 1)
                self.assertEqual(vote_data['var'][const][party], 0)
                self.assertEqual(vote_data['std'][const][party], 0)
                for m in LIST_MEASURES.keys():
                    self.assertEqual(list_measures[m]['cnt'][const][party], 1)
                    self.assertEqual(list_measures[m]['var'][const][party], 0)
                    self.assertEqual(list_measures[m]['std'][const][party], 0)
        measures = result['data'][0]['measures']
        for m in MEASURES.keys():
            self.assertEqual(measures[m]['cnt'], 1)
            self.assertEqual(measures[m]['var'], 0)
            self.assertEqual(measures[m]['std'], 0)

    def test_simulate(self):
        #Arrange
        self.s_rules["simulation_count"] = 100
        sim = simulate.Simulation(self.s_rules, [self.e_rules], self.vote_table)
        #Act
        sim.simulate()
        #Assert
        result = sim.get_results_dict()
        vote_data = result['vote_data']['sim_votes']
        list_measures = result['data'][0]['list_measures']
        for const in range(sim.num_constituencies):
            for party in range(sim.num_parties):
                self.assertGreater(vote_data['sum'][const][party], 0)
                self.assertGreater(vote_data['avg'][const][party], 0)
                self.assertGreater(vote_data['max'][const][party], 0)
                self.assertGreater(vote_data['min'][const][party], 0)
                self.assertEqual(vote_data['cnt'][const][party], 100)
                for m in LIST_MEASURES.keys():
                    self.assertEqual(list_measures[m]['cnt'][const][party], 100)
        measures = result['data'][0]['measures']
        for m in MEASURES.keys():
            self.assertEqual(measures[m]['cnt'], 100)
        self.assertEqual(result['time_data']['cnt'], 100)

    def test_simulate_with_custom_seat_specs(self):
        #Arrange
        self.s_rules["simulation_count"] = 100
        all_const = voting.ElectionRules()
        all_const["seat_spec_option"] = "all_const"
        all_adj = voting.ElectionRules()
        all_adj["seat_spec_option"] = "all_adj"
        one_const = voting.ElectionRules()
        one_const["seat_spec_option"] = "one_const"
        one_const["constituencies"] = self.vote_table["constituencies"]
        custom = voting.ElectionRules()
        custom["seat_spec_option"] = "custom"
        custom["constituencies"] = [
            {"name": "I",   "num_const_seats": 15, "num_adj_seats": 11},
            {"name": "III", "num_const_seats": 14, "num_adj_seats": 19},
            {"name": "IX", "num_const_seats": 140, "num_adj_seats": 31},
            {"name": "XXXI", "num_const_seats": 1, "num_adj_seats": 10},
            {"name": "XLII", "num_const_seats": 4, "num_adj_seats": 42},
            {"name": "MMXIX", "num_const_seats": 20, "num_adj_seats": 19},
        ]
        e_systems = [self.e_rules, all_const, all_adj, one_const, custom]
        sim = simulate.Simulation(self.s_rules, e_systems, self.vote_table)
        #Act
        sim.simulate()
        #Assert
        self.assertEqual(len(sim.e_rules[0]["constituencies"]), 3)
        self.assertEqual(len(sim.e_rules[1]["constituencies"]), 3)
        self.assertEqual(len(sim.e_rules[2]["constituencies"]), 3)
        self.assertEqual(len(sim.e_rules[3]["constituencies"]), 1)
        self.assertEqual(len(sim.e_rules[4]["constituencies"]), 3)
        result = sim.get_results_dict()
        for r in range(sim.num_rulesets):
            for m in LIST_MEASURES.keys():
                for aggr in AGGREGATES.keys():
                    self.assertEqual(
                        len(result["data"][r]["list_measures"][m][aggr]),
                        1+len(sim.e_rules[r]["constituencies"]))
