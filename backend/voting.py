#coding:utf-8
"""
This module contains the core voting system logic.
"""
from tabulate import tabulate

from table_util import entropy, add_totals
from solution_util import solution_exists
from apportion import apportion1d_general, \
    threshold_elimination_totals, threshold_elimination_constituencies
from electionRules import ElectionRules
from dictionaries import ADJUSTMENT_METHODS, DIVIDER_RULES, QUOTA_RULES

class Election:
    """A single election."""
    def __init__(self, rules, votes=None, name=''):
        self.num_constituencies = len(rules["constituencies"])
        self.num_parties = len(rules["parties"])
        self.rules = rules
        self.name = name
        self.set_votes(votes)

    def entropy(self):
        return entropy(self.m_votes, self.results, self.gen)

    def set_votes(self, votes):
        assert len(votes) == self.num_constituencies
        assert all(len(row) == self.num_parties for row in votes)
        self.m_votes = votes
        self.v_votes = [sum(x) for x in zip(*votes)]

    def get_results_dict(self):
        return {
            "rules": self.rules,
            "seat_allocations": add_totals(self.results),
            "step_by_step_demonstration": self.demonstration_table
        }

    def run(self):
        """Run an election based on current rules and votes."""
        # How many constituency seats does each party get in each constituency:
        self.const_seats_alloc = []
        # Which seats does each party get in each constituency:
        self.order = []
        # Determine total seats (const + adjustment) in each constituency:
        self.v_desired_row_sums = [
            const["num_const_seats"] + const["num_adj_seats"]
            for const in self.rules["constituencies"]
        ]
        # Determine total seats in play:
        self.total_seats = sum(self.v_desired_row_sums)

        self.run_primary_apportionment()
        self.run_threshold_elimination()
        self.run_determine_adjustment_seats()
        self.run_adjustment_apportionment()
        return self.results

    def run_primary_apportionment(self):
        """Conduct primary apportionment"""
        if self.rules["debug"]:
            print(" + Primary apportionment")

        constituencies = self.rules["constituencies"]
        parties = self.rules["parties"]

        m_allocations = []
        self.last = []
        for i in range(self.num_constituencies):
            num_seats = constituencies[i]["num_const_seats"]
            if num_seats != 0:
                alloc, _, last_in, _ = apportion1d_general(
                    v_votes=self.m_votes[i],
                    num_total_seats=num_seats,
                    prior_allocations=[],
                    rule=self.rules.get_generator("primary_divider"),
                    type_of_rule=self.rules.get_type("primary_divider"),
                    threshold=self.rules["constituency_threshold"]
                )
                assert last_in #last_in is not None because num_seats > 0
                self.last.append(last_in["active_votes"])
            else:
                alloc = [0]*self.num_parties
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
        self.m_votes_eliminated = threshold_elimination_constituencies(
            votes=self.m_votes,
            threshold=self.rules["adjustment_threshold"]
        )
        self.v_votes_eliminated = threshold_elimination_totals(
            votes=self.m_votes,
            threshold=self.rules["adjustment_threshold"]
        )

    def run_determine_adjustment_seats(self):
        """Calculate the number of adjustment seats each party gets."""
        if self.rules["debug"]:
            print(" + Determine adjustment seats")
        self.v_desired_col_sums, self.adj_seat_gen, _, _ = apportion1d_general(
            v_votes=self.v_votes,
            num_total_seats=self.total_seats,
            prior_allocations=self.v_const_seats_alloc,
            rule=self.rules.get_generator("adj_determine_divider"),
            type_of_rule=self.rules.get_type("adj_determine_divider"),
            threshold=self.rules["adjustment_threshold"]
        )
        return self.v_desired_col_sums

    def run_adjustment_apportionment(self):
        """Conduct adjustment seat apportionment."""
        if self.rules["debug"]:
            print(" + Apportion adjustment seats")
        method = ADJUSTMENT_METHODS[self.rules["adjustment_method"]]
        self.gen = self.rules.get_generator("adj_alloc_divider")
        consts = self.rules["constituencies"]

        self.solvable = solution_exists(
            votes=self.m_votes_eliminated,
            row_constraints=self.v_desired_row_sums,
            col_constraints=self.v_desired_col_sums,
            prior_allocations=self.m_const_seats_alloc)

        #Some methods return a solution violating the constraints if necessary
        try:
            self.results, self.adj_seats_info = method(
                m_votes=self.m_votes_eliminated,
                v_desired_row_sums=self.v_desired_row_sums,
                v_desired_col_sums=self.v_desired_col_sums,
                m_prior_allocations=self.m_const_seats_alloc,
                divisor_gen=self.gen,
                adj_seat_gen=self.adj_seat_gen,
                threshold=self.rules["adjustment_threshold"],
                orig_votes=self.m_votes,
                v_const_seats=[con["num_const_seats"] for con in consts],
                last=self.last #for nearest_neighbor and relative_inferiority
            )
        except (ZeroDivisionError, RuntimeError):
            self.results = self.m_const_seats_alloc
            self.adj_seats_info = None

        v_results = [sum(x) for x in zip(*self.results)]
        devs = [abs(a-b) for a, b in zip(self.v_desired_col_sums, v_results)]
        self.adj_dev = sum(devs)

        if self.adj_seats_info is not None:
            allocation_sequence, present = self.adj_seats_info
            headers, steps = present(self.rules, allocation_sequence)
            self.demonstration_table = {"headers": headers, "steps": steps}
        else:
            self.demonstration_table = {"headers": ["Not available"], "steps": []}

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
