# coding:utf-8
from unittest import TestCase
from random import uniform
from math import sqrt

import logging
import simulate
import voting
from table_util import add_totals


class StatisticsTest(TestCase):
    def setUp(self):
        self.vote_table = {
            "name": "Statistics test",
            "parties": ["A"],
            "votes":  [[1]],
            "constituencies": [
                {"name": "I",   "num_const_seats": 1, "num_adj_seats": 0},
            ],
        }
        self.e_rules = voting.ElectionRules()
        self.e_rules["parties"] = self.vote_table["parties"]
        self.e_rules["constituencies"] = self.vote_table["constituencies"]
        self.s_rules = simulate.SimulationRules()

    def test_statistics(self):
        #Arrange
        data = [
            {
                "sequence": [],
                "cnt": 0,
                "min": 0,
                "max": 0,
                "avg": 0,
                "var": 0, # d = 0
                "std": 0,
                "skw": 0, # h = 0
                "kur": 0, # c = 0
            },
            {
                "sequence": [1],
                "cnt": 1,
                "min": 1,
                "max": 1,
                "avg": 1,
                "var": 0, # d = 0
                "std": 0,
                "skw": 0, # h = 0
                "kur": 0, # c = 0
            },
            {
                "sequence": [1,1],
                "cnt": 2,
                "min": 1,
                "max": 1,
                "avg": 1,
                "var": 0, # d = 0
                "std": 0,
                "skw": 0, # h = 0
                "kur": 0, # c = 0
            },
            {
                "sequence": [1,2],
                "cnt": 2,
                "min": 1,
                "max": 2,
                "avg": 1.5,
                "var": 0.5, # d = 1/2
                "std": sqrt(0.5),
                "skw": 0, # h = 0
                "kur": 1, # c = 1/8
            },
            {
                "sequence": [1,1,1],
                "cnt": 3,
                "min": 1,
                "max": 1,
                "avg": 1,
                "var": 0, # d = 0
                "std": 0,
                "skw": 0, # h = 0
                "kur": 0, # c = 0
            },
            {
                "sequence": [1,2,3],
                "cnt": 3,
                "min": 1,
                "max": 3,
                "avg": 2,
                "var": 1, # d = 2
                "std": 1,
                "skw": 0, # h = 0
                "kur": 1.5, # c = 2
            },
            {
                "sequence": [1,2,6],
                "cnt": 3,
                "min": 1,
                "max": 6,
                "avg": 3,
                "var": 7, # d = 14
                "std": sqrt(7),
                "skw": 9/7*sqrt(3/14), # h = 18
                "kur": 1.5, # c = 98
            },
            {
                "sequence": [1,5,6],
                "cnt": 3,
                "min": 1,
                "max": 6,
                "avg": 4,
                "var": 7, # d = 14
                "std": sqrt(7),
                "skw": -9/7*sqrt(3/14), # h = -18
                "kur": 1.5, # c = 98
            },
        ]
        n = len(data)

        sim = simulate.Simulation(self.s_rules, [self.e_rules]*n, self.vote_table)
        placeholder_measure = "dev_opt" # Could use any in dictionaries.MEASURES

        #Act
        for k in range(n):
            for x in data[k]["sequence"]:
                sim.aggregate_measure(k, placeholder_measure, x)
            sim.analyze_measure(k, placeholder_measure)

        calculated_results = []
        for k in range(n):
            sequence = data[k]["sequence"]
            cnt = len(sequence)
            avg = sum(sequence)/cnt if cnt > 0 else 0
            dev2 = [(x-avg)**2 for x in sequence]
            d = sum(dev2)
            dev3 = [(x-avg)**3 for x in sequence]
            h = sum(dev3)
            dev4 = [(x-avg)**4 for x in sequence]
            c = sum(dev4)
            var = d/(cnt-1) if cnt > 1 else d
            v   = d/cnt     if cnt > 0 else d
            std = sqrt(var)
            s   = sqrt(v)
            skw = h/(cnt*s**3) if cnt*s > 0 else h
            kur = c/(cnt*s**4) if cnt*s > 0 else c # cnt*c/d**2
            calculated_results.append({
                "cnt": cnt,
                "min": min(sequence) if cnt > 0 else 0,
                "max": max(sequence) if cnt > 0 else 0,
                "avg": avg,
                "var": var,
                "std": std,
                "skw": skw,
                "kur": kur,
            })

        #Assert
        for k in range(n):
            expected = data[k]
            calculated = calculated_results[k]
            result = sim.data[k][placeholder_measure]
            for aggr in ["cnt","min","max","avg","var","std","skw","kur"]:
                self.assertEqual(
                    0,
                    round(expected[aggr]-calculated[aggr],ndigits=10),
                    f"Failed for k: {k}, aggr: {aggr}"
                )
                self.assertEqual(
                    0,
                    round(result[aggr]-calculated[aggr],ndigits=10),
                    f"Failed for k: {k}, aggr: {aggr}"
                )
                self.assertEqual(
                    expected[aggr],
                    result[aggr],
                    f"Failed for k: {k}, aggr: {aggr}"
                )
