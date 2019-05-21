#coding:utf-8
"""
This module contains the core voting system logic.
"""
from tabulate import tabulate

from util import entropy, add_totals
from apportion import apportion1d, threshold_elimination_totals, \
    threshold_elimination_constituencies
from election_rules import ElectionRules
from dictionaries import ADJUSTMENT_METHODS, ADJUSTMENT_METHOD_NAMES
from division_rules import dhondt_gen, sainte_lague_gen, \
    nordic_sainte_lague_gen, imperiali_gen, danish_gen, huntington_hill_gen

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
