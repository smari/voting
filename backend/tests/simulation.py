# coding:utf-8
from unittest import TestCase
from random import uniform

import logging
import simulate
import voting
import util


class SimulationTest(TestCase):
    def setUp(self):
        self.e_rules = voting.ElectionRules()
        self.e_rules["constituencies"] = [
            {"name": "I",   "num_const_seats": 5, "num_adj_seats": 1},
            {"name": "II",  "num_const_seats": 6, "num_adj_seats": 2},
            {"name": "III", "num_const_seats": 4, "num_adj_seats": 1},
        ]
        self.e_rules["parties"] = ["A", "B"]
        self.votes = [[500, 300], [200, 400], [350, 450]]
        self.vote_table = {
            "name": "Simulation test",
            "parties": self.e_rules["parties"],
            "votes": self.votes,
            "constituencies": self.e_rules["constituencies"],
        }
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
                for m in simulate.LIST_MEASURES.keys():
                    self.assertEqual(list_measures[m]['cnt'][const][party], 1)
                    self.assertEqual(list_measures[m]['var'][const][party], 0)
                    self.assertEqual(list_measures[m]['std'][const][party], 0)
        measures = result['data'][0]['measures']
        for m in simulate.MEASURES.keys():
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
                for m in simulate.LIST_MEASURES.keys():
                    self.assertEqual(list_measures[m]['cnt'][const][party], 1)
                    self.assertEqual(list_measures[m]['var'][const][party], 0)
                    self.assertEqual(list_measures[m]['std'][const][party], 0)
        measures = result['data'][0]['measures']
        for m in simulate.MEASURES.keys():
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
                for m in simulate.LIST_MEASURES.keys():
                    self.assertEqual(list_measures[m]['cnt'][const][party], 100)
        measures = result['data'][0]['measures']
        for m in simulate.MEASURES.keys():
            self.assertEqual(measures[m]['cnt'], 100)
        self.assertEqual(result['time_data']['cnt'], 100)
