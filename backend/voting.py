#coding:utf-8
"""
This module contains the core voting system logic.
"""
import random
import json
from copy import copy
from tabulate import tabulate
from util import load_votes, load_constituencies, entropy
from apportion import apportion1d, constituency_seat_allocation, \
    threshold_elimination_totals, threshold_elimination_constituencies
from rules import Rules
from simulate import SimulationRules # TODO: This belongs elsewhere.
from methods import *
import io

from methods.alternating_scaling import *
from methods.icelandic_law import *
from methods.monge import *
from methods.relative_inferiority import *
from methods.relative_superiority import *

def dhondt_gen():
    """Generate a d'Hondt divider sequence: 1, 2, 3..."""
    n = 1
    while True:
        yield n
        n += 1

def sainte_lague_gen():
    """Generate a Sainte-Lague divider sequence: 1, 3, 5..."""
    n = 1
    while True:
        yield n
        n += 2

def nordic_sainte_lague_gen():
    """Generate a Nordic Sainte-Lague divide sequence: 1.4, 3, 5..."""
    yield 1.4
    n = 3
    while True:
        yield n
        n += 2

DIVIDER_RULES = {
    "dhondt": dhondt_gen,
    "sainte-lague": sainte_lague_gen,
    "nordic": nordic_sainte_lague_gen
}

DIVIDER_RULE_NAMES = {
    "dhondt": "D'Hondt's method",
    "sainte-lague": "Sainte-Laguë method",
    "nordic": "Nordic Sainte-Laguë variant"
}


class ElectionRules(Rules):
    """A set of rules for an election or a simulation to follow."""

    def __init__(self):
        super(ElectionRules, self).__init__()
        self.value_rules = {
            "primary_divider": DIVIDER_RULES.keys(),
            "adjustment_divider": DIVIDER_RULES.keys(),
            "adjustment_method": ADJUSTMENT_METHODS.keys(),
        }
        self.range_rules = {
            "adjustment_threshold": [0.0, 1.0]
        }
        self.list_rules = [
            "constituency_seats", "constituency_adjustment_seats",
            "constituency_names", "parties"
        ]

        # Election rules
        self["primary_divider"] = "dhondt"
        self["adjustment_divider"] = "dhondt"
        self["adjustment_threshold"] = 0.05
        self["adjustment_method"] = "icelandic-law"
        self["constituency_seats"] = []
        self["constituency_adjustment_seats"] = []
        self["constituency_names"] = []
        self["parties"] = []

        # Display rules
        self["debug"] = False
        self["show_entropy"] = False
        self["output"] = "simple"

    def __setitem__(self, key, value):
        if key == "constituencies":
            value = load_constituencies(value)
            self["constituency_names"] = [x["name"] for x in value]
            self["constituency_seats"] = [x["num_constituency_seats"]
                                          for x in value]
            self["constituency_adjustment_seats"] = [x["num_adjustment_seats"]
                                                     for x in value]

        super(ElectionRules, self).__setitem__(key, value)

    def get_generator(self, div):
        """Fetch a generator from divider rules."""
        method = self[div]
        if method in DIVIDER_RULES.keys():
            return DIVIDER_RULES[method]
        else:
            raise ValueError("%s is not a known divider" % div)


class Election:
    """A single election."""
    def __init__(self, rules, votes=None):
        self.rules = rules
        #self.m_votes = votes
        self.set_votes(votes)
        self.order = []
        self.log = []

    def entropy(self):
        return entropy(self.m_votes, self.results, self.gen)

    def set_votes(self, votes):
        assert(len(votes) == len(self.rules["constituency_names"]))
        assert(all([len(x) == len(self.rules["parties"])
                    for x in votes]))
        self.m_votes = votes

    def get_results_dict(self):
        return {
            "rules": self.rules,
            "seat_allocations": self.results,
        }

    def run(self):
        """Run an election based on current rules and votes."""
        # How many seats does each party get in each constituency:
        self.m_allocations = []
        # Which seats does each party get in each constituency:
        self.m_seats = []
        # Determine total seats (const + adjustment) in each constituency:
        self.v_total_seats = [sum(x) for x in
                              zip(self.rules["constituency_seats"],
                                  self.rules["constituency_adjustment_seats"])
                             ]
        # Determine total seats in play:
        self.total_seats = sum(self.v_total_seats)

        self.run_primary_apportionment()
        self.run_threshold_elimination()
        self.run_determine_adjustment_seats()
        self.run_adjustment_apportionment()
        return self.results

    def run_primary_apportionment(self):
        """Conduct primary apportionment"""
        if self.rules["debug"]:
            print(" + Primary apportionment")
        m_allocations, v_seatcount = self.primary_apportionment(self.m_votes)
        self.m_allocations = m_allocations
        self.v_cur_allocations = v_seatcount

    def run_threshold_elimination(self):
        if self.rules["debug"]:
            print(" + Threshold elimination")
        threshold = self.rules["adjustment_threshold"]
        v_elim_votes = threshold_elimination_totals(self.m_votes, threshold)
        m_elim_votes = threshold_elimination_constituencies(self.m_votes,
                                                            threshold)
        self.v_votes_eliminated = v_elim_votes
        self.m_votes_eliminated = m_elim_votes

    def run_determine_adjustment_seats(self):
        """
        Calculate the number of adjusment seats each party gets.
        """
        if self.rules["debug"]:
            print(" + Determine adjustment seats")
        v_votes = self.v_votes_eliminated
        gen = self.rules.get_generator("adjustment_divider")
        v_priors = self.v_cur_allocations
        v_seats, divs = apportion1d(v_votes, self.total_seats, v_priors, gen)
        self.v_adjustment_seats = v_seats
        return v_seats

    def run_adjustment_apportionment(self):
        if self.rules["debug"]:
            print(" + Apportion adjustment seats")
        method = ADJUSTMENT_METHODS[self.rules["adjustment_method"]]
        gen = self.rules.get_generator("adjustment_divider")

        results = method(self.m_votes_eliminated,
                         self.v_total_seats,
                         self.v_adjustment_seats,
                         self.m_allocations,
                         gen,
                         self.rules["adjustment_threshold"],
                         orig_votes=self.m_votes)

        self.results = results
        self.gen = gen

        # header = ["Constituency"]
        # header.extend(self.rules["parties"])
        # print "\n=== %s ===" %
        #    (ADJUSTMENT_METHOD_NAMES[self.rules["adjustment_method"]])
        # data = [[self.rules["constituency_names"][c]]+results[c] for c in
        #         range(len(self.rules["constituency_names"]))]
        # print tabulate(data, header, "simple")

        if self.rules["show_entropy"]:
            print("\nEntropy: %s" % self.entropy())

    def primary_apportionment(self, m_votes):
        """Do primary allocation of seats for all constituencies"""
        gen = self.rules.get_generator("primary_divider")
        const = self.rules["constituency_seats"]
        parties = self.rules["parties"]

        m_allocations = []
        for i in range(len(const)):
            num_seats = const[i]
            rounds, seats = constituency_seat_allocation(m_votes[i], num_seats,
                                                         gen)
            v_allocations = [seats.count(p) for p in range(len(parties))]
            m_allocations.append(v_allocations)
            self.order.append(seats)

        # Useful:
        # print tabulate([[parties[x] for x in y] for y in self.order])

        v_seatcount = [sum([x[i] for x in m_allocations]) for i in range(len(parties))]

        return m_allocations, v_seatcount


ADJUSTMENT_METHODS = {
    "alternating-scaling": alternating_scaling,
    "relative-superiority": relative_superiority,
    "relative-inferiority": relative_inferiority,
    "monge": monge,
    "icelandic-law": icelandic_apportionment,
}

ADJUSTMENT_METHOD_NAMES = {
    "alternating-scaling": "Alternating-Scaling Method",
    "relative-superiority": "Relative Superiority Method",
    "relative-inferiority": "Relative Inferiority Method",
    "monge": "Monge algorithm",
    "icelandic-law": "Icelandic law 24/2000 (Kosningar til Alþingis)"
}



# TODO: These functions should be elsewhere.

def get_capabilities_dict():
    return {
        "election_rules": ElectionRules(),
        "simulation_rules": SimulationRules(),
        "capabilities": {
            "divider_rules": DIVIDER_RULE_NAMES,
            "adjustment_methods": ADJUSTMENT_METHOD_NAMES,
        },
        "presets": get_presets()
    }

def get_presets():
    from os import listdir
    from os.path import isfile, join
    presetsdir = "../data/presets/"
    try:        
        files = [f for f in listdir(presetsdir) if isfile(join(presetsdir, f))
                 and f.endswith('.json')]
    except Exception as e:
        print("Presets directory read failure: %s" % (e))
        files = []
    pr = []
    for f in files:        
        try:
            with open(presetsdir+f) as json_file:
                data = json.load(json_file)
        except  json.decoder.JSONDecodeError:
            data = {'error': 'Problem parsing json, please fix "{}"'.format(
                presetsdir+f)}
        pr.append(data)
    return pr

def run_script(rules):
    if type(rules) != dict:
        return {"error": "Incorrect script format."}

    if rules["action"] not in ["simulation", "election"]:
        return {"error": "Script action must be election or simulation."}

    if rules["action"] == "election":
        rs = ElectionRules()
        if "election_rules" not in rules:
            return {"error": "No election rules supplied."}

        rs.update(rules["election_rules"])

        if not "votes" in rs:
            return {"error": "No votes supplied"}

        election = Election(rs, rs["votes"])
        election.run()

        return election

    else:
        return {"error": "Not implemented."}


if __name__ == "__main__":
    pass
