# from voting import Election, SIMULATION_VARIATES
from rules import Rules
from math import sqrt, exp
from random import betavariate, uniform
from copy import copy, deepcopy
from util import add_totals

import voting
import io
import json
from numpy import zeros_like
from datetime import datetime, timedelta


def beta_params(mean, var_param):
    alpha = mean*(1/var_param**2 - 1)
    beta = alpha*(1/mean - 1)
    return alpha, beta

def beta_distribution(m_ref_votes, var_param):
    """
    Generate a set of votes with beta distribution,
    using 'm_ref_votes' as reference.
    """
    m_votes = []
    m_shares = []
    ref_totals = [sum(c) for c in m_ref_votes]

    for c in range(len(m_ref_votes)):
        s = 0
        m_votes.append([])
        for p in range(len(m_ref_votes[c])):
            mean_beta_distr = m_ref_votes[c][p]/float(ref_totals[c])
            if mean_beta_distr > 0:
                var_beta = var_param*mean_beta_distr*(1-mean_beta_distr)
                alpha, beta = beta_params(mean_beta_distr, var_param)
                share = betavariate(alpha, beta)
            else:
                share = 0
            m_votes[c].append(int(share*ref_totals[c]))
        shares = [v/float(sum(m_votes[c])) for v in m_votes[c]]
        m_shares.append(shares)

    return m_votes, m_shares

GENERATING_METHODS = {
    "beta": beta_distribution
}

GENERATING_METHOD_NAMES = {
    "beta": "Beta distribution"
}

MEASURES = {
    "entropy":         "Entropy",
    "entropy_ratio":   "Entropy Ratio",
    "dev_opt":         "Seat Deviation from Optimal",
    "dev_law":         "Seat Deviation from Icelandic Law",
    "dev_ind_const":   "Seat Deviation from Independent Constituencies",
    "dev_one_const":   "Seat Deviation from Single Constituency",
    "dev_all_adj":     "Seat Deviation from All Adjustment Seats",
    "loosemore_hanby": "Loosemore-Hanby Index",
    "sainte_lague":    "Sainte-Lague minsum Index",
    "dhondt_min":      "d'Hondt maxmin Index",
    "dhondt_sum":      "d'Hondt minsum Index",
    "adj_dev":         "Adjustment seat deviation from determined",
}

LIST_MEASURES = {
    "const_seats":   "constituency seats",
    "adj_seats":     "adjustment seats",
    "total_seats":   "constituency and adjustment seats combined",
    "seat_shares":   "floating number of seats proportional to vote shares",
    "dev_opt":       "deviation from optimal solution",
    "dev_law":       "deviation from official law method",
    "dev_ind_const": "deviation from Independent Constituencies",
    "dev_one_const": "deviation from Single Constituency",
    "dev_all_adj":   "deviation from All Adjustment Seats"
}

VOTE_MEASURES = {
    "simul_votes":   "votes in simulations",
    "simul_shares":  "shares in simulations",
}

def error(avg, ref):
    """
    Compare average of generated votes to reference votes to test the
    quality of the simulation.
    """
    num_consts = len(avg)
    num_parties = len(avg[0])
    s = 0
    for c in range(num_consts):
        for p in range(num_parties):
            if type(ref) is list:
                s += abs(avg[c][p] - ref[c][p])
            else:
                s += abs(avg[c][p] - ref)
    return s/(num_consts*num_parties)

def dev(results, ref):
    """Calculate seat deviation of results compared to reference results."""
    d = 0
    for c in range(len(results)):
        for p in range(len(results[c])):
            d += abs(results[c][p] - ref[c][p])
    return d

def votes_to_change(election):
    """
    Find how many additional votes each individual list must receive
    for the results of the given election to change.
    """
    ref_results = election.results
    ref_votes = election.m_votes
    votes_to_change = []
    votes = deepcopy(ref_votes)
    for c in range(len(ref_results)):
        votes_to_change.append([])
        for p in range(len(ref_results[c])):
            if ref_votes[c][p] == 0:
                votes_to_change[c].append(None)
                continue
            a = 0
            b = int(0.1*votes[c][p])
            d = 0
            while d == 0:
                votes[c][p] = ref_votes[c][p]+b
                election = voting.Election(election.rules, votes)
                results = election.run()
                d = dev(results, ref_results)
                if d == 0:
                    a = copy(b)
                    b = int(sqrt(2)*b)
            m = b-a
            x = 0
            while m > 1:
                x = int(m*sqrt(0.5) + a)
                votes[c][p] = ref_votes[c][p]+x
                election = voting.Election(election.rules, votes)
                results = election.run()
                d = dev(results, ref_results)
                if d == 0:
                    a = copy(x)
                else:
                    b = copy(x)
                m = b-a
            votes_to_change[c].append(b)
            votes[c][p] = ref_votes[c][p]

    return votes_to_change


class SimulationRules(Rules):
    def __init__(self):
        super(SimulationRules, self).__init__()
        # Simulation rules
        self["simulate"] = False
        self["simulation_count"] = 10000
        self["gen_method"] = "beta"


class Simulation:
    """Simulate a set of elections."""
    def __init__(self, sim_rules, e_rules, m_votes, var_param=0.1):
        self.sim_rules = sim_rules
        self.e_rules = e_rules
        self.ref_votes = add_totals(m_votes)
        self.ref_shares = [[v/c[-1] for v in c] for c in self.ref_votes]
        self.variate = self.sim_rules["gen_method"]
        self.var_param = var_param
        self.iteration = 0
        self.terminate = False
        self.iteration_time = timedelta(0)

        self.no_total_simulations = self.sim_rules["simulation_count"]
        self.no_rulesets = len(self.e_rules)
        self.no_constituencies = len(m_votes)
        self.no_parties = len(m_votes[0])
        self.data = []
        self.list_data = []
        for ruleset in range(self.no_rulesets):
            self.data.append({})
            for measure in MEASURES.keys():
                self.data[ruleset][measure] = {
                    "sum": 0, "sqs": 0,
                    "avg": 0, "var": 0
                }
            self.list_data.append({})
            for measure in LIST_MEASURES.keys():
                self.list_data[ruleset][measure] = []
                for c in range(1+self.no_constituencies):
                    self.list_data[ruleset][measure].append([])
                    for p in range(1+self.no_parties):
                        self.list_data[ruleset][measure][c].append({
                            "sum": 0, "sqs": 0,
                            "avg": 0, "var": 0
                        })
        self.data.append({})
        self.list_data.append({})
        for measure in VOTE_MEASURES.keys():
            self.list_data[-1][measure] = []
            for c in range(1+self.no_constituencies):
                self.list_data[-1][measure].append([])
                for p in range(1+self.no_parties):
                    self.list_data[-1][measure][c].append({
                        "sum": 0, "sqs": 0,
                        "avg": 0, "var": 0
                    })

    def aggregate_list(self, ruleset, measure, cnstncy, party, value):
        self.list_data[ruleset][measure][cnstncy][party]["sum"] += value
        self.list_data[ruleset][measure][cnstncy][party]["sqs"] += value**2

    def analyze_list(self, ruleset, measure, cnstncy, party, count):
        s = float(self.list_data[ruleset][measure][cnstncy][party]["sum"])
        t = float(self.list_data[ruleset][measure][cnstncy][party]["sqs"])
        avg = s/count
        var = (t - s*avg) / (count-1)
        self.list_data[ruleset][measure][cnstncy][party]["avg"] = avg
        self.list_data[ruleset][measure][cnstncy][party]["var"] = var

    def aggregate_measure(self, ruleset, measure, value):
        self.data[ruleset][measure]["sum"] += value
        self.data[ruleset][measure]["sqs"] += value**2

    def analyze_measure(self, ruleset, measure, count):
        s = float(self.data[ruleset][measure]["sum"])
        t = float(self.data[ruleset][measure]["sqs"])
        avg = s/count
        var = (t - s*avg) / (count-1)
        self.data[ruleset][measure]["avg"] = avg
        self.data[ruleset][measure]["var"] = var

    def gen_votes(self):
        """
        Generate votes similar to given votes using the given
        generating method.
        """
        gen = GENERATING_METHODS[self.variate]
        while True:
            rv = [v[:-1] for v in self.ref_votes[:-1]]
            votes, shares = gen(rv, self.var_param)

            for c in range(self.no_constituencies):
                for p in range(self.no_parties):
                    self.aggregate_list(-1, "simul_votes", c, p, votes[c][p])
                    self.aggregate_list(-1, "simul_shares", c, p, shares[c][p])
                self.aggregate_list(-1, "simul_votes", c, -1, sum(votes[c]))
                self.aggregate_list(-1, "simul_shares", c, -1, sum(shares[c]))
            total_votes = [sum(x) for x in zip(*votes)]
            total_votes.append(sum(total_votes))
            total_shares = [t/total_votes[-1] if total_votes[-1] > 0 else 0
                                for t in total_votes]
            for p in range(1+self.no_parties):
                self.aggregate_list(-1, "simul_votes", -1, p, total_votes[p])
                self.aggregate_list(-1, "simul_shares", -1, p, total_shares[p])

            yield votes, shares

    def test_generated(self):
        """Analysis of generated votes."""
        n = self.no_total_simulations
        var_beta_distr = []
        for c in range(1+self.no_constituencies):
            var_beta_distr.append([])
            for p in range(1+self.no_parties):
                for measure in VOTE_MEASURES.keys():
                    self.analyze_list(-1, measure, c, p, n)
                var_beta_distr[c].append(self.var_param
                                        *self.ref_shares[c][p]
                                        *(self.ref_shares[c][p]-1))
        simul_shares = {
            aggregate: [
                [
                    self.list_data[-1]["simul_shares"][c][p][aggregate]
                    for p in range(self.no_parties)
                ]
                for c in range(self.no_constituencies)
            ]
            for aggregate in ["avg", "var"]
        }
        self.data[-1]["simul_shares"] = {
            "err_avg": error(simul_shares["avg"], self.ref_shares),
            "err_var": error(simul_shares["var"], var_beta_distr)
        }

    def method_analysis(self, idx, votes, results, entropy):
        """Various tests to determine the quality of the given method."""
        ref_rules = sim_ref_rules(self.e_rules[idx])
        opt_rules = ref_rules["opt"]
        law_rules = ref_rules["law"]
        ind_const_rules = ref_rules["ind_const"]
        one_const_rules = ref_rules["one_const"]
        all_adj_rules = ref_rules["all_adj"]

        opt_election = voting.Election(opt_rules, votes)
        opt_results = opt_election.run()
        opt_entropy = opt_election.entropy()
        entropy_ratio = exp(entropy - opt_entropy)
        self.aggregate_measure(idx, "entropy_ratio", entropy_ratio)
        dev_opt = dev(results, opt_results)
        self.aggregate_measure(idx, "dev_opt", dev_opt)

        law_election = voting.Election(law_rules, votes)
        law_results = law_election.run()
        dev_law = dev(results, law_results)
        self.aggregate_measure(idx, "dev_law", dev_law)

        ind_const_election = voting.Election(ind_const_rules, votes)
        ind_const_results = ind_const_election.run()
        dev_ind_const = dev(results, ind_const_results)
        self.aggregate_measure(idx, "dev_ind_const", dev_ind_const)

        v_votes = [[sum([c[p] for c in votes]) for p in range(len(votes[0]))]]
        one_const_election = voting.Election(one_const_rules, v_votes)
        one_const_results = one_const_election.run()
        v_results = [sum(x) for x in zip(*results)]
        dev_one_const = dev([v_results], one_const_results)
        self.aggregate_measure(idx, "dev_one_const", dev_one_const)

        all_adj_election = voting.Election(all_adj_rules, v_votes)
        all_adj_results = all_adj_election.run()
        dev_all_adj = dev([v_results], all_adj_results)
        self.aggregate_measure(idx, "dev_all_adj", dev_all_adj)

        bi_seat_shares = deepcopy(votes)
        const_mult = [1]*len(bi_seat_shares)
        party_mult = [1]*len(bi_seat_shares[0])
        seats_party_opt = [sum(x) for x in zip(*opt_results)]
        error = 1
        while round(error, 5) != 0.0:
            const_mult = [self.seats_total_const[idx][c]/sum(bi_seat_shares[c])
                            for c in range(len(self.seats_total_const[idx]))]
            s = [sum(x) for x in zip(*bi_seat_shares)]
            party_mult = [seats_party_opt[p]/s[p] if s[p] != 0 else 1
                            for p in range(len(seats_party_opt))]
            for c in range(len(bi_seat_shares)):
                for p in range(len(bi_seat_shares[c])):
                    r = uniform(0.0, 1.0)
                    bi_seat_shares[c][p] *= 1 - r + r*const_mult[c]*party_mult[p]
            error = sum([abs(1-cm) for cm in const_mult]) + sum([abs(1-pm) for pm in party_mult])

        try:
            assert(all([sum([c[p] for c in bi_seat_shares]) == seats_party_opt[p]
                        for p in range(len(seats_party_opt))]))
        except AssertionError:
            pass
        try:
            assert(all([sum(bi_seat_shares[c]) == self.seats_total_const[idx][c]
                        for c in range(len(self.seats_total_const[idx]))]))
        except AssertionError:
            pass

        total_seats = sum([sum(c) for c in results])
        lh = sum([sum([abs(bi_seat_shares[c][p]-results[c][p])
                    for p in range(len(results[c]))])
                    for c in range(len(results))]) / (2*total_seats)
        self.aggregate_measure(idx, "loosemore_hanby", lh)

        scale = 1
        stl = sum([sum([(bi_seat_shares[c][p]-results[c][p])**2/bi_seat_shares[c][p]
                    if bi_seat_shares[c][p] != 0 else 0
                    for p in range(len(results[c]))])
                    for c in range(len(results))]) * scale
        self.aggregate_measure(idx, "sainte_lague", stl)

        dh_min_factors = [bi_seat_shares[c][p]/float(results[c][p])
                          if results[c][p] != 0 else 10000000000000000
                          for p in range(len(results[c]))
                          for c in range(len(results))]
        dh_min = min(dh_min_factors)
        self.aggregate_measure(idx, "dhondt_min", dh_min)

        dh_sum = sum([max(0, bi_seat_shares[c][p]-results[c][p])/bi_seat_shares[c][p] if bi_seat_shares[c][p] != 0 else 10000000000000000000000
                        for p in range(len(results[c]))
                        for c in range(len(results))])
        self.aggregate_measure(idx, "dhondt_sum", dh_sum)

    def analysis(self):
        """Calculate averages and variances of various quality measures."""
        n = self.iteration
        for ruleset in range(self.no_rulesets):
            for measure in MEASURES.keys():
                self.analyze_measure(ruleset, measure, n)
            for c in range(1+self.no_constituencies):
                for p in range(1+self.no_parties):
                    for measure in LIST_MEASURES.keys():
                        self.analyze_list(ruleset, measure, c, p, n)

    def simulate(self):
        """Simulate many elections."""
        gen = self.gen_votes()
        self.seats_total_const = []
        self.ref_total_seats = []
        self.ref_const_seats = []
        self.ref_adj_seats = []
        for ruleset in range(self.no_rulesets):
            votes = [v[:-1] for v in self.ref_votes[:-1]]
            election = voting.Election(self.e_rules[ruleset], votes)
            results = election.run()
            self.seats_total_const.append(election.v_total_seats)
            ref_total_seats = add_totals(results)
            self.ref_total_seats.append(ref_total_seats)
            ref_const_seats = add_totals(election.m_const_seats_alloc)
            self.ref_const_seats.append(ref_const_seats)
            ref_adj_seats = [[ref_total_seats[c][p]-ref_const_seats[c][p]
                                for p in range(len(ref_total_seats[c]))]
                                for c in range(len(ref_total_seats))]
            self.ref_adj_seats.append(ref_adj_seats)
        for i in range(self.no_total_simulations):
            round_start = datetime.now()
            self.iteration = i + 1
            if self.terminate:
                break
            votes, shares = next(gen)
            for ruleset in range(self.no_rulesets):
                election = voting.Election(self.e_rules[ruleset], votes)
                results = election.run()
                const_seats_alloc = add_totals(election.m_const_seats_alloc)
                total_seats_alloc = add_totals(results)
                for c in range(1+self.no_constituencies):
                    for p in range(1+self.no_parties):
                        cs  = const_seats_alloc[c][p]
                        ts  = total_seats_alloc[c][p]
                        adj = ts-const_seats_alloc[c][p]
                        sh  = ts/total_seats_alloc[c][-1]
                        self.aggregate_list(ruleset, "const_seats", c, p, cs)
                        self.aggregate_list(ruleset, "total_seats", c, p, ts)
                        self.aggregate_list(ruleset, "adj_seats", c, p, adj)
                        self.aggregate_list(ruleset, "seat_shares", c, p, sh)
                entropy = election.entropy()
                self.aggregate_measure(ruleset, "entropy", entropy)
                self.aggregate_measure(ruleset, "adj_dev", election.adj_dev)
                self.method_analysis(ruleset, votes, results, entropy)
            round_end = datetime.now()
            self.iteration_time = round_end - round_start
        self.analysis()
        self.test_generated()


    def get_results_dict(self):
        self.analysis()
        return {
            "testnames": [rules["name"] for rules in self.e_rules],
            "methods": [rules["adjustment_method"] for rules in self.e_rules],
            "measures": [MEASURES[measure] for measure in MEASURES.keys()],
            "data": [
                [
                    self.data[ruleset][measure]["avg"]
                    for ruleset in range(self.no_rulesets)
                ]
                for measure in MEASURES.keys()
            ]
        }


def sim_ref_rules(rs):

    opt_rs = voting.ElectionRules()
    law_rs = voting.ElectionRules()
    ind_const_rs = voting.ElectionRules()
    one_const_rs = voting.ElectionRules()
    all_adj_rs = voting.ElectionRules()

    opt_rs.update(rs)
    opt_rs["adjustment_method"] = "alternating-scaling"
    law_rs["adjustment_method"] = "icelandic-law"
    law_rs["primary_divider"] = "dhondt"
    law_rs["adj_determine_divider"] = "dhondt"
    law_rs["adj_alloc_divider"] = "dhondt"
    law_rs["adjustment_threshold"] = 0.05
    law_rs["constituency_seats"] = rs["constituency_seats"]
    law_rs["constituency_adjustment_seats"] = rs["constituency_adjustment_seats"]
    law_rs["constituency_names"] = rs["constituency_names"]
    law_rs["parties"] = rs["parties"]
    ind_const_rs.update(rs)
    ind_const_rs["constituency_seats"] = copy(rs["constituency_seats"])
    ind_const_rs["constituency_adjustment_seats"] = []
    for i in range(len(rs["constituency_seats"])):
        ind_const_rs["constituency_seats"][i] += rs["constituency_adjustment_seats"][i]
        ind_const_rs["constituency_adjustment_seats"].append(0)
    one_const_rs.update(rs)
    one_const_rs["constituency_seats"] = [sum(rs["constituency_seats"])]
    one_const_rs["constituency_adjustment_seats"] = [sum(rs["constituency_adjustment_seats"])]
    one_const_rs["constituency_names"] = ["All"]
    all_adj_rs.update(one_const_rs)
    all_adj_rs["constituency_seats"] = [0]
    all_adj_rs["constituency_adjustment_seats"] = [one_const_rs["constituency_seats"][0]
                        + one_const_rs["constituency_adjustment_seats"][0]]

    ref = {"opt": opt_rs,
            "law": law_rs,
            "ind_const": ind_const_rs,
            "one_const": one_const_rs,
            "all_adj": all_adj_rs}

    return ref

def run_script_simulation(rules):
    srs = SimulationRules()
    srs.update(rules["simulation_rules"])

    rs = voting.ElectionRules()
    rs.update(rules["election_rules"])

    if not "ref_votes" in rules:
        return {"error": "No reference votes supplied."}

    election = voting.Election(rs, rules["ref_votes"])

    sim = Simulation(srs, election)
    sim.simulate()

    return sim
