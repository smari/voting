#coding:utf-8
"""
This module contains the core voting system logic.
"""
import json
from tabulate import tabulate
from util import load_votes, load_constituencies, entropy, add_totals
from apportion import apportion1d, threshold_elimination_totals, \
    threshold_elimination_constituencies
from rules import Rules
from methods import *
import io

from methods.var_alt_scal import *
from methods.alternating_scaling import *
from methods.icelandic_law import *
from methods.monge import *
from methods.nearest_neighbor import *
from methods.relative_superiority import *
from methods.norwegian_law import *
from methods.norwegian_icelandic import *
from methods.pure_vote_ratios import *
from methods.opt_entropy import opt_entropy
from methods.switching import *

def dhondt_gen():
    """Generate a d'Hondt divider sequence: 1, 2, 3..."""
    n = 1.0
    while True:
        yield n
        n += 1.0

def sainte_lague_gen():
    """Generate a Sainte-Lague divider sequence: 1, 3, 5..."""
    n = 1.0
    while True:
        yield n
        n += 2.0

def nordic_sainte_lague_gen():
    """Generate a Nordic Sainte-Lague divide sequence: 1.4, 3, 5..."""
    yield 1.4
    n = 3.0
    while True:
        yield n
        n += 2.0

def imperiali_gen():
    """Generate Imperiali divider sequence: 1, 1.5, 2, 2.5,..."""
    n = 1.0
    while True:
        yield n
        n += 0.5

def danish_gen():
    """Generate Danish divider sequence: 0.33, 1.33, 2.33,..."""
    n = 0.33
    while True:
        yield n
        n += 1.0

def huntington_hill_gen():
    """Generate Huntington-Hill divider sequence; modified for hh(0) -> \inf"""
    n = 0
    yield 10000000000
    while True:
        n += 1
        yield sqrt(n*(n+1))

DIVIDER_RULES = {
    "dhondt": dhondt_gen,
    "sainte-lague": sainte_lague_gen,
    "nordic": nordic_sainte_lague_gen,
    "imperiali": imperiali_gen,
    "danish": danish_gen,
    "huntington-hill": huntington_hill_gen,
}

DIVIDER_RULE_NAMES = {
    "dhondt": "D'Hondt's method",
    "sainte-lague": "Sainte-Laguë method",
    "nordic": "Nordic Sainte-Laguë variant",
    "imperiali": "Imeriali method",
    "danish": "Danish method",
    "huntington-hill": "Huntington-Hill method",
}


class ElectionRules(Rules):
    """A set of rules for an election to follow."""

    def __init__(self):
        super(ElectionRules, self).__init__()
        self.value_rules = {
            "primary_divider": DIVIDER_RULES.keys(),
            "adj_determine_divider": DIVIDER_RULES.keys(),
            "adj_alloc_divider": DIVIDER_RULES.keys(),
            "adjustment_method": ADJUSTMENT_METHODS.keys(),
        }
        self.range_rules = {
            "adjustment_threshold": [0, 100]
        }
        self.list_rules = [
            "constituency_seats", "constituency_adjustment_seats",
            "constituency_names", "parties"
        ]

        self["name"] = "My test"

        # Election rules
        self["primary_divider"] = "dhondt"
        self["adj_determine_divider"] = "dhondt"
        self["adj_alloc_divider"] = "dhondt"
        self["adjustment_threshold"] = 5
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
        self.num_constituencies = len(rules["constituency_adjustment_seats"])
        assert(len(rules["constituency_seats"]) == self.num_constituencies)
        assert(len(rules["constituency_names"]) == self.num_constituencies)
        self.rules = rules
        self.set_votes(votes)

    def entropy(self):
        return entropy(self.m_votes, self.results, self.gen)

    def set_votes(self, votes):
        assert(len(votes) == self.num_constituencies)
        assert(all([len(x) == len(self.rules["parties"])
                    for x in votes]))
        self.m_votes = votes
        self.v_votes = [sum(x) for x in zip(*votes)]

    def get_results_dict(self):
        return {
            "rules": self.rules,
            "seat_allocations": add_totals(self.results),
        }

    def run(self):
        """Run an election based on current rules and votes."""
        # How many constituency seats does each party get in each constituency:
        self.const_seats_alloc = []
        # Which seats does each party get in each constituency:
        self.order = []
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

        gen = self.rules.get_generator("primary_divider")
        const_seats = self.rules["constituency_seats"]
        parties = self.rules["parties"]

        m_allocations = []
        self.last = []
        for i in range(len(const_seats)):
            num_seats = const_seats[i]
            if num_seats != 0:
                alloc, div = apportion1d(self.m_votes[i], num_seats, [0]*len(parties), gen)
                self.last.append(div[2])
            else:
                alloc = [0]*len(parties)
                self.last.append(0)
            m_allocations.append(alloc)
            # self.order.append(seats)

        # Useful:
        # print tabulate([[parties[x] for x in y] for y in self.order])

        v_allocations = [sum(x) for x in zip(*m_allocations)]

        self.m_const_seats_alloc = m_allocations
        self.v_const_seats_alloc = v_allocations

    def run_threshold_elimination(self):
        """Eliminate parties that do not reach the adjustment threshold."""
        if self.rules["debug"]:
            print(" + Threshold elimination")
        threshold = self.rules["adjustment_threshold"]*0.01
        v_elim_votes = threshold_elimination_totals(self.m_votes, threshold)
        m_elim_votes = threshold_elimination_constituencies(self.m_votes,
                                                            threshold)
        self.v_votes_eliminated = v_elim_votes
        self.m_votes_eliminated = m_elim_votes

    def run_determine_adjustment_seats(self):
        """Calculate the number of adjustment seats each party gets."""
        if self.rules["debug"]:
            print(" + Determine adjustment seats")
        v_votes = self.v_votes_eliminated
        gen = self.rules.get_generator("adj_determine_divider")
        v_priors = self.v_const_seats_alloc
        v_seats, _ = apportion1d(v_votes, self.total_seats, v_priors, gen)
        self.v_adjustment_seats = v_seats
        return v_seats

    def run_adjustment_apportionment(self):
        """Conduct adjustment seat apportionment."""
        if self.rules["debug"]:
            print(" + Apportion adjustment seats")
        method = ADJUSTMENT_METHODS[self.rules["adjustment_method"]]
        gen = self.rules.get_generator("adj_alloc_divider")

        results, asi = method(self.m_votes_eliminated,
            self.v_total_seats,
            self.v_adjustment_seats,
            self.m_const_seats_alloc,
            gen,
            self.rules["adjustment_threshold"]*0.01,
            orig_votes=self.m_votes,
            last=self.last)

        self.adj_seats_info = asi

        self.results = results
        self.gen = gen

        v_results = [sum(x) for x in zip(*results)]
        devs = [abs(a-b) for a, b in zip(self.v_adjustment_seats, v_results)]
        self.adj_dev = sum(devs)

        if self.rules["show_entropy"]:
            print("\nEntropy: %s" % self.entropy())


ADJUSTMENT_METHODS = {
    "var-alt-scal": var_alt_scal,
    "alternating-scaling": alternating_scaling,
    "relative-superiority": relative_superiority,
    "nearest-neighbor": nearest_neighbor,
    "monge": monge,
    "icelandic-law": icelandic_apportionment,
    "norwegian-law": norwegian_apportionment,
    "norwegian-icelandic": norw_ice_apportionment,
    "opt-entropy": opt_entropy,
    "switching": switching,
    "pure-vote-ratios": pure_vote_ratios_apportionment,
}

ADJUSTMENT_METHOD_NAMES = {
    "alternating-scaling": "Alternating-Scaling Method",
    "relative-superiority": "Relative Superiority Method",
    "nearest-neighbor": "Nearest Neighbor Method",
    "monge": "Monge algorithm",
    "icelandic-law": "Icelandic law 24/2000 (Kosningar til Alþingis)",
    "norwegian-law": "Norwegian law",
    "norwegian-icelandic": "Norwegian-Icelandic variant",
    "switching": "Switching Method",
    "pure-vote-ratios": "Pure Vote Ratios"
}



def run_script_election(rules):
    rs = ElectionRules()
    if "election_rules" not in rules:
        return {"error": "No election rules supplied."}

    rs.update(rules["election_rules"])

    if not "votes" in rs:
        return {"error": "No votes supplied"}

    election = Election(rs, rs["votes"])
    election.run()

    return election

if __name__ == "__main__":
    pass
