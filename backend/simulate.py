# from voting import Election, SIMULATION_VARIATES
from rules import Rules
from math import sqrt, exp
from random import betavariate
from copy import copy, deepcopy
from util import add_totals, matrix_subtraction, find_shares

import voting
import io
import json
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

    return m_votes

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
    "adj_dev":         "Adjustment seat deviation from constraints",
}

LIST_MEASURES = {
    "const_seats":   "constituency seats",
    "adj_seats":     "adjustment seats",
    "total_seats":   "constituency and adjustment seats combined",
    "seat_shares":   "total seats scaled to a total of 1 for each constituency",
    "dev_opt":       "deviation from optimal solution",
    "dev_law":       "deviation from official law method",
    "dev_ind_const": "deviation from Independent Constituencies",
    "dev_one_const": "deviation from Single Constituency",
    "dev_all_adj":   "deviation from All Adjustment Seats"
}

VOTE_MEASURES = {
    "sim_votes":  "votes in simulations",
    "sim_shares": "shares in simulations",
}

AGGREGATES = {
    "cnt": "number of elements",
    "sum": "sum of elements",
    "sqs": "sum of squares",
    "avg": "average",
    "var": "variance",
    "std": "standard deviation"
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
        self["simulation_count"] = 1000
        self["gen_method"] = "beta"


class Simulation:
    """Simulate a set of elections."""
    def __init__(self, sim_rules, e_rules, m_votes, var_param=0.1):
        self.num_total_simulations = sim_rules["simulation_count"]
        self.num_rulesets = len(e_rules)
        self.num_constituencies = len(m_votes)
        self.num_parties = len(m_votes[0])
        assert(all([len(c) == self.num_parties for c in m_votes]))
        assert(all([
            self.num_constituencies == len(ruleset["constituency_names"])
            and self.num_constituencies == len(ruleset["constituency_seats"])
            and self.num_constituencies == len(ruleset["constituency_adjustment_seats"])
            and self.num_parties == len(ruleset["parties"])
            for ruleset in e_rules
        ]))
        self.sim_rules = sim_rules
        self.e_rules = e_rules
        self.base_votes = m_votes
        self.xtd_votes = add_totals(self.base_votes)
        self.xtd_vote_shares = find_shares(self.xtd_votes)
        self.variate = self.sim_rules["gen_method"]
        self.var_param = var_param
        self.iteration = 0
        self.terminate = False
        self.iteration_time = timedelta(0)

        self.data = []
        self.list_data = []
        for ruleset in range(self.num_rulesets):
            self.data.append({})
            for measure in MEASURES.keys():
                self.data[ruleset][measure] = {
                    aggr: 0
                    for aggr in AGGREGATES.keys()
                }
            self.list_data.append({})
            for measure in LIST_MEASURES.keys():
                self.list_data[ruleset][measure] = {}
                for aggr in AGGREGATES.keys():
                    self.list_data[ruleset][measure][aggr] = []
                    for c in range(self.num_constituencies+1):
                        self.list_data[ruleset][measure][aggr].append([0]*(self.num_parties+1))

        self.data.append({})
        self.list_data.append({})
        for measure in VOTE_MEASURES.keys():
            self.list_data[-1][measure] = {}
            for aggr in AGGREGATES.keys():
                self.list_data[-1][measure][aggr] = []
                for c in range(self.num_constituencies+1):
                    self.list_data[-1][measure][aggr].append([0]*(self.num_parties+1))

        self.run_initial_elections()

    def aggregate_list(self, ruleset, measure, const, party, value):
        self.list_data[ruleset][measure]["cnt"][const][party] += 1
        self.list_data[ruleset][measure]["sum"][const][party] += value
        self.list_data[ruleset][measure]["sqs"][const][party] += value**2

    def analyze_list(self, ruleset, measure, const, party):
        n = float(self.list_data[ruleset][measure]["cnt"][const][party])
        s = float(self.list_data[ruleset][measure]["sum"][const][party])
        t = float(self.list_data[ruleset][measure]["sqs"][const][party])
        avg = s/n                 if n>0 else 0
        var = (t - s*avg) / (n-1) if n>1 else 0
        std = sqrt(var)
        self.list_data[ruleset][measure]["avg"][const][party] = avg
        self.list_data[ruleset][measure]["var"][const][party] = var
        self.list_data[ruleset][measure]["std"][const][party] = std

    def aggregate_measure(self, ruleset, measure, value):
        self.data[ruleset][measure]["cnt"] += 1
        self.data[ruleset][measure]["sum"] += value
        self.data[ruleset][measure]["sqs"] += value**2

    def analyze_measure(self, ruleset, measure):
        n = float(self.data[ruleset][measure]["cnt"])
        s = float(self.data[ruleset][measure]["sum"])
        t = float(self.data[ruleset][measure]["sqs"])
        avg = s/n                 if n>0 else 0
        var = (t - s*avg) / (n-1) if n>1 else 0
        std = sqrt(var)
        self.data[ruleset][measure]["avg"] = avg
        self.data[ruleset][measure]["var"] = var
        self.data[ruleset][measure]["std"] = std

    def run_initial_elections(self):
        self.base_allocations = []
        for r in range(self.num_rulesets):
            election = voting.Election(self.e_rules[r], self.base_votes)
            xtd_total_seats = add_totals(election.run())
            xtd_const_seats = add_totals(election.m_const_seats_alloc)
            xtd_adj_seats = matrix_subtraction(xtd_total_seats, xtd_const_seats)
            xtd_seat_shares = find_shares(xtd_total_seats)
            self.base_allocations.append({
                "xtd_const_seats": xtd_const_seats,
                "xtd_adj_seats": xtd_adj_seats,
                "xtd_total_seats": xtd_total_seats,
                "xtd_seat_shares": xtd_seat_shares
            })

    def gen_votes(self):
        """
        Generate votes similar to given votes using the given
        generating method.
        """
        gen = GENERATING_METHODS[self.variate]
        while True:
            votes = gen(self.base_votes, self.var_param)
            xtd_votes  = add_totals(votes)
            xtd_shares = find_shares(xtd_votes)
            for c in range(self.num_constituencies+1):
                for p in range(self.num_parties+1):
                    self.aggregate_list(-1, "sim_votes", c, p, xtd_votes[c][p])
                    self.aggregate_list(-1, "sim_shares", c, p, xtd_shares[c][p])

            yield votes

    def test_generated(self):
        """Analysis of generated votes."""
        var_beta_distr = []
        for c in range(1+self.num_constituencies):
            var_beta_distr.append([])
            for p in range(1+self.num_parties):
                for measure in VOTE_MEASURES.keys():
                    self.analyze_list(-1, measure, c, p)
                var_beta_distr[c].append(self.var_param
                                        *self.xtd_vote_shares[c][p]
                                        *(self.xtd_vote_shares[c][p]-1))
        sim_shares = self.list_data[-1]["sim_shares"]
        self.data[-1]["sim_shares"] = {
            "err_avg": error(sim_shares["avg"], self.xtd_vote_shares),
            "err_var": error(sim_shares["var"], var_beta_distr)
        }

    def collect_list_measures(self, ruleset, results, election):
        const_seats_alloc = add_totals(election.m_const_seats_alloc)
        total_seats_alloc = add_totals(results)
        for c in range(1+self.num_constituencies):
            for p in range(1+self.num_parties):
                cs  = const_seats_alloc[c][p]
                ts  = total_seats_alloc[c][p]
                adj = ts-const_seats_alloc[c][p]
                sh  = float(ts)/total_seats_alloc[c][-1]
                self.aggregate_list(ruleset, "const_seats", c, p, cs)
                self.aggregate_list(ruleset, "total_seats", c, p, ts)
                self.aggregate_list(ruleset, "adj_seats", c, p, adj)
                self.aggregate_list(ruleset, "seat_shares", c, p, sh)

    def collect_general_measures(self, ruleset, votes, results, election):
        """Various tests to determine the quality of the given method."""
        self.aggregate_measure(ruleset, "adj_dev", election.adj_dev)
        opt_results = self.entropy(ruleset, votes, election.entropy())
        self.deviation_measures(ruleset, votes, results, opt_results)
        self.other_measures(ruleset, votes, results, opt_results)

    def entropy(self, ruleset, votes, entropy):
        opt_rules = generate_opt_ruleset(self.e_rules[ruleset])
        opt_election = voting.Election(opt_rules, votes)
        opt_results = opt_election.run()
        entropy_ratio = exp(entropy - opt_election.entropy())
        self.aggregate_measure(ruleset, "entropy_ratio", entropy_ratio)
        self.aggregate_measure(ruleset, "entropy", entropy)
        return opt_results

    def deviation_measures(self, ruleset, votes, results, opt_results):
        self.deviation(ruleset, "opt", None, results, opt_results)
        self.deviation(ruleset, "law", votes, results)
        self.deviation(ruleset, "ind_const", votes, results)
        v_votes = [[sum([c[p] for c in votes]) for p in range(self.num_parties)]]
        v_results = [sum(x) for x in zip(*results)]
        self.deviation(ruleset, "one_const", v_votes, [v_results])
        self.deviation(ruleset, "all_adj", v_votes, [v_results])

    def other_measures(self, ruleset, votes, results, opt_results):
        bi_seat_shares = self.calculate_bi_seat_shares(ruleset, votes, opt_results)
        scale = 1.0/sum([
            sum([1.0/s for s in c])
            for c in bi_seat_shares
        ])
        self.loosemore_hanby(ruleset, results, bi_seat_shares)
        self.sainte_lague(ruleset, results, bi_seat_shares, scale)
        self.dhondt_min(ruleset, results, bi_seat_shares)
        self.dhondt_sum(ruleset, results, bi_seat_shares, scale)

    def deviation(self, ruleset, option, votes, reference_results, results=None):
        if results == None:
            rules = generate_comparison_rules(self.e_rules[ruleset], option)
            results = voting.Election(rules, votes).run()
        deviation = dev(reference_results, results)
        self.aggregate_measure(ruleset, "dev_"+option, deviation)

    def calculate_bi_seat_shares(self, ruleset, votes, opt_results):
        election = voting.Election(self.e_rules[ruleset], self.base_votes)
        election.run()
        v_total_seats = election.v_total_seats

        bi_seat_shares = deepcopy(votes)
        seats_party_opt = [sum(x) for x in zip(*opt_results)]
        rein = 0
        error = 1
        while round(error, 5) != 0.0:
            error = 0
            for c in range(self.num_constituencies):
                s = sum(bi_seat_shares[c])
                if s != 0:
                    mult = float(v_total_seats[c])/s
                    error += abs(1-mult)
                    for p in range(self.num_parties):
                        bi_seat_shares[c][p] *= rein + mult*(1-rein)
            for p in range(self.num_parties):
                s = sum([c[p] for c in bi_seat_shares])
                if s != 0:
                    mult = float(seats_party_opt[p])/s
                    error += abs(1-mult)
                    for c in range(self.num_constituencies):
                        bi_seat_shares[c][p] *= rein + mult*(1-rein)

        try:
            assert(all([sum([c[p] for c in bi_seat_shares]) == seats_party_opt[p]
                        for p in range(self.num_parties)]))
        except AssertionError:
            pass
        try:
            assert(all([sum(bi_seat_shares[c]) == v_total_seats[c]
                        for c in range(self.num_constituencies)]))
        except AssertionError:
            pass

        return bi_seat_shares

    def loosemore_hanby(self, ruleset, results, bi_seat_shares):
        total_seats = sum([sum(c) for c in results])
        scale = 1.0/total_seats
        lh = sum([
            abs(bi_seat_shares[c][p]-results[c][p])
            for p in range(self.num_parties)
            for c in range(self.num_constituencies)
        ])
        lh *= scale
        self.aggregate_measure(ruleset, "loosemore_hanby", lh)

    def sainte_lague(self, ruleset, results, bi_seat_shares, scale):
        stl = sum([
            (bi_seat_shares[c][p]-results[c][p])**2/bi_seat_shares[c][p]
            if bi_seat_shares[c][p] != 0 else 0
            for p in range(self.num_parties)
            for c in range(self.num_constituencies)
        ])
        stl *= scale
        self.aggregate_measure(ruleset, "sainte_lague", stl)

    def dhondt_min(self, ruleset, results, bi_seat_shares):
        dh_min = min([
            bi_seat_shares[c][p]/float(results[c][p])
            if results[c][p] != 0 else 10000000000000000
            for p in range(self.num_parties)
            for c in range(self.num_constituencies)
        ])
        self.aggregate_measure(ruleset, "dhondt_min", dh_min)

    def dhondt_sum(self, ruleset, results, bi_seat_shares, scale):
        dh_sum = sum([
            max(0, bi_seat_shares[c][p]-results[c][p])/bi_seat_shares[c][p]
            if bi_seat_shares[c][p] != 0 else 10000000000000000000000
            for p in range(self.num_parties)
            for c in range(self.num_constituencies)
        ])
        dh_sum *= scale
        self.aggregate_measure(ruleset, "dhondt_sum", dh_sum)

    def analysis(self):
        """Calculate averages and variances of various quality measures."""
        for ruleset in range(self.num_rulesets):
            for measure in MEASURES.keys():
                self.analyze_measure(ruleset, measure)
            for c in range(1+self.num_constituencies):
                for p in range(1+self.num_parties):
                    for measure in LIST_MEASURES.keys():
                        self.analyze_list(ruleset, measure, c, p)

    def simulate(self):
        """Simulate many elections."""
        gen = self.gen_votes()
        for i in range(self.num_total_simulations):
            round_start = datetime.now()
            if self.terminate:
                break
            self.iteration = i + 1
            votes = next(gen)
            for ruleset in range(self.num_rulesets):
                election = voting.Election(self.e_rules[ruleset], votes)
                results = election.run()
                self.collect_list_measures(ruleset, results, election)
                self.collect_general_measures(ruleset, votes, results, election)
            round_end = datetime.now()
            self.iteration_time = round_end - round_start
        self.analysis()
        self.test_generated()


    def get_results_dict(self):
        self.analysis()
        return {
            "testnames": [rules["name"] for rules in self.e_rules],
            "methods": [rules["adjustment_method"] for rules in self.e_rules],
            "measures": MEASURES,
            "list_measures": LIST_MEASURES,
            "vote_measures": VOTE_MEASURES,
            "aggregates": AGGREGATES,
            "data": [
                {
                    "name": self.e_rules[ruleset]["name"],
                    "method": self.e_rules[ruleset]["adjustment_method"],
                    "measures": self.data[ruleset],
                    "list_measures": self.list_data[ruleset]
                }
                for ruleset in range(self.num_rulesets)
            ],
            "vote_data": self.list_data[-1]
        }

def generate_comparison_rules(ruleset, option="all"):
    if option == "opt":
        return generate_opt_ruleset(ruleset)
    if option == "law":
        return generate_law_ruleset(ruleset)
    if option == "ind_const":
        return generate_ind_const_ruleset(ruleset)
    if option == "one_const":
        return generate_one_const_ruleset(ruleset)
    if option == "all_adj":
        return generate_all_adj_ruleset(ruleset)
    if option == "all":
        return {
            "opt":       generate_opt_ruleset(ruleset),
            "law":       generate_law_ruleset(ruleset),
            "ind_const": generate_ind_const_ruleset(ruleset),
            "one_const": generate_one_const_ruleset(ruleset),
            "all_adj":   generate_all_adj_ruleset(ruleset)
        }
    return None

def generate_opt_ruleset(ruleset):
    ref_rs = voting.ElectionRules()
    ref_rs.update(ruleset)
    ref_rs["adjustment_method"] = "alternating-scaling"
    return ref_rs

def generate_law_ruleset(ruleset):
    ref_rs = voting.ElectionRules()
    ref_rs.update(ruleset)
    ref_rs["adjustment_method"] = "icelandic-law"
    ref_rs["primary_divider"] = "dhondt"
    ref_rs["adj_determine_divider"] = "dhondt"
    ref_rs["adj_alloc_divider"] = "dhondt"
    ref_rs["adjustment_threshold"] = 0.05
    return ref_rs

def generate_ind_const_ruleset(ruleset):
    ref_rs = voting.ElectionRules()
    ref_rs.update(ruleset)
    ref_rs["constituency_seats"] = copy(ruleset["constituency_seats"])
    ref_rs["constituency_adjustment_seats"] = []
    for i in range(len(ruleset["constituency_seats"])):
        ref_rs["constituency_seats"][i] += ruleset["constituency_adjustment_seats"][i]
        ref_rs["constituency_adjustment_seats"].append(0)
    return ref_rs

def generate_one_const_ruleset(ruleset):
    ref_rs = voting.ElectionRules()
    ref_rs.update(ruleset)
    ref_rs["constituency_seats"] = [sum(ruleset["constituency_seats"])]
    ref_rs["constituency_adjustment_seats"] = [sum(ruleset["constituency_adjustment_seats"])]
    ref_rs["constituency_names"] = ["All"]
    return ref_rs

def generate_all_adj_ruleset(ruleset):
    ref_rs = voting.ElectionRules()
    ref_rs.update(ruleset)
    ref_rs["constituency_names"] = ["All"]
    ref_rs["constituency_seats"] = [0]
    ref_rs["constituency_adjustment_seats"] \
        = [sum(ruleset["constituency_seats"]) \
           + sum(ruleset["constituency_adjustment_seats"])]
    return ref_rs

def run_script_simulation(rules):
    srs = SimulationRules()
    srs.update(rules["simulation_rules"])

    rs = voting.ElectionRules()
    rs.update(rules["election_rules"])

    if not "ref_votes" in rules:
        return {"error": "No reference votes supplied."}

    election = voting.Election(rs, rules["ref_votes"])

    sim = Simulation(srs, election, rules["ref_votes"])
    sim.simulate()

    return sim
