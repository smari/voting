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

        self.no_rulesets = len(self.e_rules)
        self.data = []
        for ruleset in range(self.no_rulesets):
            self.data.append({})
            for measure in MEASURES.keys():
                self.data[ruleset][measure] = {
                    "sum": 0, "sqs": 0,
                    "avg": 0, "var": 0
                }

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
        self.simul_votes = zeros_like(self.ref_votes)
        self.sq_simul_votes = zeros_like(self.ref_votes)
        self.simul_shares = zeros_like(self.ref_votes)
        self.sq_simul_shares = zeros_like(self.ref_votes)
        gen = GENERATING_METHODS[self.variate]
        while True:
            rv = [v[:-1] for v in self.ref_votes[:-1]]
            votes, shares = gen(rv, self.var_param)

            for c in range(len(votes)):
                for p in range(len(votes[c])):
                    self.simul_votes[c][p] += votes[c][p]
                    self.sq_simul_votes[c][p] += votes[c][p]**2
                    self.simul_shares[c][p] += shares[c][p]
                    self.sq_simul_shares[c][p] += shares[c][p]**2
                self.simul_votes[c][-1] += sum(votes[c])
                self.sq_simul_votes[c][-1] += sum(votes[c])**2
                self.simul_shares[c][-1] += sum(shares[c])
                self.sq_simul_shares[c][-1] += sum(shares[c])**2
            total_votes = [sum(x) for x in zip(*votes)]
            total_votes.append(sum(total_votes))
            total_shares = [t/total_votes[-1] if total_votes[-1] > 0 else 0
                                for t in total_votes]
            for p in range(len(total_votes)):
                self.simul_votes[-1][p] += total_votes[p]
                self.sq_simul_votes[-1][p] += total_votes[p]**2
                self.simul_shares[-1][p] += total_shares[p]
                self.sq_simul_shares[-1][p] += total_shares[p]**2

            yield votes, shares

    def test_generated(self):
        """Analysis of generated votes."""
        n = self.sim_rules["simulation_count"]
        self.avg_simul_votes = [[v/n for v in c] for c in self.simul_votes]
        self.avg_simul_shares = [[s/n for s in c] for c in self.simul_shares]
        var_simul_votes = []
        var_simul_shares = []
        var_beta_distr = []

        for c in range(len(self.ref_votes)):
            var_simul_votes.append([])
            var_simul_shares.append([])
            var_beta_distr.append([])
            for p in range(len(self.ref_votes[c])):
                variance_votes = (self.sq_simul_votes[c][p]
                                    -self.simul_votes[c][p]**2/n) / (n-1)
                variance_shares = (self.sq_simul_shares[c][p]
                                    -self.simul_shares[c][p]**2/n) / (n-1)
                var_simul_votes[c].append(variance_votes)
                var_simul_shares[c].append(variance_shares)

                var_beta_distr[c].append(self.var_param
                                        *self.ref_shares[c][p]
                                        *(self.ref_shares[c][p]-1))

        self.var_simul_votes = var_simul_votes
        self.var_simul_shares = var_simul_shares
        self.error_avg_simul_shares = error(self.avg_simul_shares,
                                            self.ref_shares)
        self.error_var_simul_shares = error(var_simul_shares, var_beta_distr)


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
        self.entropy_ratio[idx] += entropy_ratio
        self.sq_entropy_ratio[idx] += entropy_ratio**2
        self.aggregate_measure(idx, "entropy_ratio", entropy_ratio)
        dev_opt = dev(results, opt_results)
        self.dev_opt[idx] += dev_opt
        self.sq_dev_opt[idx] += dev_opt**2
        self.aggregate_measure(idx, "dev_opt", dev_opt)

        law_election = voting.Election(law_rules, votes)
        law_results = law_election.run()
        dev_law = dev(results, law_results)
        self.dev_law[idx] += dev_law
        self.sq_dev_law[idx] += dev_law**2
        self.aggregate_measure(idx, "dev_law", dev_law)

        ind_const_election = voting.Election(ind_const_rules, votes)
        ind_const_results = ind_const_election.run()
        dev_ind_const = dev(results, ind_const_results)
        self.dev_ind_const[idx] += dev_ind_const
        self.sq_dev_ind_const[idx] += dev_ind_const**2
        self.aggregate_measure(idx, "dev_ind_const", dev_ind_const)

        v_votes = [[sum([c[p] for c in votes]) for p in range(len(votes[0]))]]
        one_const_election = voting.Election(one_const_rules, v_votes)
        one_const_results = one_const_election.run()
        v_results = [sum(x) for x in zip(*results)]
        dev_one_const = dev([v_results], one_const_results)
        self.dev_one_const[idx] += dev_one_const
        self.sq_dev_one_const[idx] += dev_one_const**2
        self.aggregate_measure(idx, "dev_one_const", dev_one_const)

        all_adj_election = voting.Election(all_adj_rules, v_votes)
        all_adj_results = all_adj_election.run()
        dev_all_adj = dev([v_results], all_adj_results)
        self.dev_all_adj[idx] += dev_all_adj
        self.sq_dev_all_adj[idx] += dev_all_adj**2
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
        self.loosemore_hanby[idx] += lh
        self.sq_loosemore_hanby[idx] += lh**2
        self.aggregate_measure(idx, "loosemore_hanby", lh)

        scale = 1
        stl = sum([sum([(bi_seat_shares[c][p]-results[c][p])**2/bi_seat_shares[c][p]
                    if bi_seat_shares[c][p] != 0 else 0
                    for p in range(len(results[c]))])
                    for c in range(len(results))]) * scale
        self.sainte_lague[idx] += stl
        self.sq_sainte_lague[idx] += stl**2
        self.aggregate_measure(idx, "sainte_lague", stl)

        dh_min_factors = [bi_seat_shares[c][p]/float(results[c][p])
                          if results[c][p] != 0 else 10000000000000000
                          for p in range(len(results[c]))
                          for c in range(len(results))]
        dh_min = min(dh_min_factors)
        self.dhondt_min[idx] += dh_min
        self.sq_dhondt_min[idx] += dh_min**2
        self.aggregate_measure(idx, "dhondt_min", dh_min)

        dh_sum = sum([max(0, bi_seat_shares[c][p]-results[c][p])/bi_seat_shares[c][p] if bi_seat_shares[c][p] != 0 else 10000000000000000000000
                        for p in range(len(results[c]))
                        for c in range(len(results))])
        self.dhondt_sum[idx] += dh_sum
        self.sq_dhondt_sum[idx] += dh_sum**2
        self.aggregate_measure(idx, "dhondt_sum", dh_sum)

    def analysis(self):
        """Calculate averages and variances of various quality measures."""
        n = self.iteration
        self.avg_const_seats, self.var_const_seats = [], []
        self.avg_adj_seats, self.var_adj_seats = [], []
        self.avg_total_seats, self.var_total_seats = [], []
        self.avg_seat_shares, self.var_seat_shares = [], []
        self.avg_entropy = [e/n for e in self.entropy]
        self.avg_entropy_ratio = [er/n for er in self.entropy_ratio]
        self.avg_dev_opt = [do/n for do in self.dev_opt]
        self.avg_dev_law = [dl/n for dl in self.dev_law]
        self.avg_dev_ind_const = [dic/n for dic in self.dev_ind_const]
        self.avg_dev_one_const = [doc/n for doc in self.dev_one_const]
        self.avg_dev_all_adj = [daa/n for daa in self.dev_all_adj]
        self.avg_loosemore_hanby = [lh/n for lh in self.loosemore_hanby]
        self.avg_sainte_lague = [stl/n for stl in self.sainte_lague]
        self.avg_dhondt_min = [dhm/n for dhm in self.dhondt_min]
        self.avg_dhondt_sum = [dhs/n for dhs in self.dhondt_sum]
        self.avg_adj_dev = [ad/n for ad in self.adj_dev]
        self.var_entropy = []
        self.var_entropy_ratio = []
        self.var_dev_opt = []
        self.var_dev_law = []
        self.var_dev_ind_const = []
        self.var_dev_one_const = []
        self.var_dev_all_adj = []
        self.var_loosemore_hanby = []
        self.var_sainte_lague = []
        self.var_dhondt_min = []
        self.var_dhondt_sum = []
        self.var_adj_dev = []
        for r in range(len(self.e_rules)):
            for measure in MEASURES.keys():
                self.analyze_measure(r, measure, n)

            self.avg_const_seats.append([[s/n for s in c] for c in self.const_seats[r]])
            self.avg_adj_seats.append([[s/n for s in c] for c in self.adj_seats[r]])
            self.avg_total_seats.append([[s/n for s in c] for c in self.total_seats[r]])
            self.avg_seat_shares.append([[s/n for s in c] for c in self.seat_shares[r]])
            self.var_const_seats.append([])
            self.var_adj_seats.append([])
            self.var_total_seats.append([])
            self.var_seat_shares.append([])
            for c in range(len(self.ref_votes)):
                self.var_const_seats[r].append([])
                self.var_adj_seats[r].append([])
                self.var_total_seats[r].append([])
                self.var_seat_shares[r].append([])
                for p in range(len(self.ref_votes[c])):
                    variance = (self.sq_const_seats[r][c][p] - self.const_seats[r][c][p]**2/n) / (n-1)
                    self.var_const_seats[r][c].append(variance)
                    variance = (self.sq_adj_seats[r][c][p] - self.adj_seats[r][c][p]**2/n) / (n-1)
                    self.var_adj_seats[r][c].append(variance)
                    variance = (self.sq_total_seats[r][c][p] - self.total_seats[r][c][p]**2/n) / (n-1)
                    self.var_total_seats[r][c].append(variance)
                    variance = abs(self.sq_seat_shares[r][c][p] - self.seat_shares[r][c][p]**2/n) / (n-1)
                    self.var_seat_shares[r][c].append(variance)

            self.var_entropy.append((self.sq_entropy[r] - self.entropy[r]**2/n) / (n-1))
            self.var_entropy_ratio.append((self.sq_entropy_ratio[r] - self.entropy_ratio[r]**2/n) / (n-1))
            self.var_dev_opt.append((self.sq_dev_opt[r] - self.dev_opt[r]**2/n) / (n-1))
            self.var_dev_law.append((self.sq_dev_law[r] - self.dev_law[r]**2/n) / (n-1))
            self.var_dev_ind_const.append((self.sq_dev_ind_const[r] - self.dev_ind_const[r]**2/n) / (n-1))
            self.var_dev_one_const.append((self.sq_dev_one_const[r] - self.dev_one_const[r]**2/n) / (n-1))
            self.var_dev_all_adj.append((self.sq_dev_all_adj[r] - self.dev_all_adj[r]**2/n) / (n-1))
            self.var_loosemore_hanby.append((self.sq_loosemore_hanby[r] - self.loosemore_hanby[r]**2/n) / (n-1))
            self.var_sainte_lague.append((self.sq_sainte_lague[r] - self.sainte_lague[r]**2/n) / (n-1))
            self.var_dhondt_min.append((self.sq_dhondt_min[r] - self.dhondt_min[r]**2/n) / (n-1))
            self.var_dhondt_sum.append((self.sq_dhondt_sum[r] - self.dhondt_sum[r]**2/n) / (n-1))
            self.var_adj_dev.append((self.sq_adj_dev[r] - self.adj_dev[r]**2/n) / (n-1))

    def simulate(self):
        """Simulate many elections."""
        gen = self.gen_votes()
        num_rules = len(self.e_rules)
        self.const_seats, self.sq_const_seats = [], []
        self.adj_seats, self.sq_adj_seats = [], []
        self.total_seats, self.sq_total_seats = [], []
        self.seat_shares, self.sq_seat_shares = [], []
        for r in range(num_rules):
            self.const_seats.append(zeros_like(self.ref_votes))
            self.sq_const_seats.append(zeros_like(self.ref_votes))
            self.adj_seats.append(zeros_like(self.ref_votes))
            self.sq_adj_seats.append(zeros_like(self.ref_votes))
            self.total_seats.append(zeros_like(self.ref_votes))
            self.sq_total_seats.append(zeros_like(self.ref_votes))
            self.seat_shares.append(zeros_like(self.ref_votes))
            self.sq_seat_shares.append(zeros_like(self.ref_votes))
        self.entropy, self.sq_entropy = [0]*num_rules, [0]*num_rules
        self.entropy_ratio = [0]*num_rules
        self.sq_entropy_ratio = [0]*num_rules
        self.dev_opt, self.sq_dev_opt = [0]*num_rules, [0]*num_rules
        self.dev_law, self.sq_dev_law = [0]*num_rules, [0]*num_rules
        self.dev_ind_const = [0]*num_rules
        self.sq_dev_ind_const = [0]*num_rules
        self.dev_one_const = [0]*num_rules
        self.sq_dev_one_const = [0]*num_rules
        self.dev_all_adj, self.sq_dev_all_adj = [0]*num_rules, [0]*num_rules
        self.loosemore_hanby = [0]*num_rules
        self.sq_loosemore_hanby = [0]*num_rules
        self.sainte_lague, self.sq_sainte_lague = [0]*num_rules, [0]*num_rules
        self.dhondt_min, self.sq_dhondt_min = [0]*num_rules, [0]*num_rules
        self.dhondt_sum, self.sq_dhondt_sum = [0]*num_rules, [0]*num_rules
        self.adj_dev, self.sq_adj_dev = [0]*num_rules, [0]*num_rules
        self.seats_total_const = []
        self.ref_total_seats = []
        self.ref_const_seats = []
        self.ref_adj_seats = []
        for r in range(len(self.e_rules)):
            votes = [v[:-1] for v in self.ref_votes[:-1]]
            election = voting.Election(self.e_rules[r], votes)
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
        for i in range(self.sim_rules["simulation_count"]):
            round_start = datetime.now()
            self.iteration = i + 1
            if self.terminate:
                break
            votes, shares = next(gen)
            for r in range(len(self.e_rules)):
                election = voting.Election(self.e_rules[r], votes)
                results = election.run()
                const_seats_alloc = add_totals(election.m_const_seats_alloc)
                total_seats_alloc = add_totals(results)
                for c in range(len(self.total_seats[r])):
                    for p in range(len(self.total_seats[r][c])):
                        self.const_seats[r][c][p] += const_seats_alloc[c][p]
                        self.sq_const_seats[r][c][p] += const_seats_alloc[c][p]**2
                        adj = total_seats_alloc[c][p]-const_seats_alloc[c][p]
                        self.adj_seats[r][c][p] += adj
                        self.sq_adj_seats[r][c][p] += adj**2
                        self.total_seats[r][c][p] += total_seats_alloc[c][p]
                        self.sq_total_seats[r][c][p] += total_seats_alloc[c][p]**2
                        sh = total_seats_alloc[c][p]/total_seats_alloc[c][-1]
                        self.seat_shares[r][c][p] += sh
                        self.sq_seat_shares[r][c][p] += sh**2
                entropy = election.entropy()
                self.entropy[r] += entropy
                self.sq_entropy[r] += entropy**2
                self.aggregate_measure(r, "entropy", entropy)
                self.adj_dev[r] += election.adj_dev
                self.sq_adj_dev[r] += election.adj_dev**2
                self.aggregate_measure(r, "adj_dev", election.adj_dev)
                self.method_analysis(r, votes, results, entropy)
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
