# from voting import Election, SIMULATION_VARIATES
import logging
import json
from datetime import datetime, timedelta
from math import sqrt, exp
from copy import copy, deepcopy

from table_util import matrix_subtraction, scale_matrix, add_totals, find_xtd_shares
from excel_util import simulation_to_xlsx
from rules import Rules
from dictionaries import GENERATING_METHODS
from dictionaries import MEASURES, DEVIATION_MEASURES, STANDARDIZED_MEASURES, \
    LIST_MEASURES, VOTE_MEASURES, AGGREGATES
import voting
from electionHandler import ElectionHandler

logging.basicConfig(filename='logs/simulate.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

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
    assert(len(results) == len(ref))
    d = 0
    for c in range(len(results)):
        assert(len(results[c]) == len(ref[c]))
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
        self.value_rules = {
            #Fair share constraints:
            "row_constraints": {True, False},
            "col_constraints": {True, False},
        }
        self["simulate"] = False
        self["simulation_count"] = 1000
        self["gen_method"] = "beta"
        self["distribution_parameter"] = 100
        self["row_constraints"] = True
        self["col_constraints"] = True


class Simulation:
    """Simulate a set of elections."""
    def __init__(self, sim_rules, e_rules, vote_table):
        self.e_handler = ElectionHandler(vote_table, e_rules)
        self.e_rules = [el.rules for el in self.e_handler.elections]
        self.num_rulesets = len(self.e_rules)
        self.vote_table = self.e_handler.vote_table
        self.constituencies = self.vote_table["constituencies"]
        self.num_constituencies = len(self.constituencies)
        self.parties = self.vote_table["parties"]
        self.num_parties = len(self.parties)
        self.base_votes = self.vote_table["votes"]
        self.xtd_votes = add_totals(self.base_votes)
        self.xtd_vote_shares = find_xtd_shares(self.xtd_votes)
        self.sim_rules = sim_rules
        self.num_total_simulations = self.sim_rules["simulation_count"]
        self.variate = self.sim_rules["gen_method"]
        self.stbl_param = self.sim_rules["distribution_parameter"]
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
            num_constituencies = len(self.e_rules[ruleset]["constituencies"])
            self.list_data.append({})
            for measure in LIST_MEASURES.keys():
                self.list_data[ruleset][measure] = {}
                for aggr in AGGREGATES.keys():
                    self.list_data[ruleset][measure][aggr] = []
                    for c in range(num_constituencies+1):
                        self.list_data[ruleset][measure][aggr].append([0]*(self.num_parties+1))

        self.data.append({})
        self.data[-1]["time"] = {}
        for aggr in AGGREGATES.keys():
            self.data[-1]["time"][aggr] = 0
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
        if (self.list_data[ruleset][measure]["cnt"][const][party] > 1):
            if (value > self.list_data[ruleset][measure]["max"][const][party]):
                self.list_data[ruleset][measure]["max"][const][party] = value
            if (value < self.list_data[ruleset][measure]["min"][const][party]):
                self.list_data[ruleset][measure]["min"][const][party] = value
        else:
            self.list_data[ruleset][measure]["max"][const][party] = value
            self.list_data[ruleset][measure]["min"][const][party] = value

    def analyze_list(self, ruleset, measure, const, party):
        n = float(self.list_data[ruleset][measure]["cnt"][const][party])
        s = float(self.list_data[ruleset][measure]["sum"][const][party])
        t = float(self.list_data[ruleset][measure]["sqs"][const][party])
        avg = s/n                 if n>0 else 0
        var = (t - s*avg) / (n-1) if n>1 else 0
        if -0.0000001 < var and var < 0:
            var = 0

        # TODO: remove when resolved.
        try:
            std = sqrt(var)
        except ValueError:
            logging.error(f'Error calculating square root of: {var}')
            raise

        self.list_data[ruleset][measure]["avg"][const][party] = avg
        self.list_data[ruleset][measure]["var"][const][party] = var
        self.list_data[ruleset][measure]["std"][const][party] = std

    def aggregate_measure(self, ruleset, measure, value):
        self.data[ruleset][measure]["cnt"] += 1
        self.data[ruleset][measure]["sum"] += value
        self.data[ruleset][measure]["sqs"] += value**2
        if (self.data[ruleset][measure]["cnt"] > 1):
            if (value > self.data[ruleset][measure]["max"]):
                self.data[ruleset][measure]["max"] = value
            if (value < self.data[ruleset][measure]["min"]):
                self.data[ruleset][measure]["min"] = value
        else:
            self.data[ruleset][measure]["max"] = value
            self.data[ruleset][measure]["min"] = value

    def analyze_measure(self, ruleset, measure):
        n = float(self.data[ruleset][measure]["cnt"])
        s = float(self.data[ruleset][measure]["sum"])
        t = float(self.data[ruleset][measure]["sqs"])
        avg = s/n                 if n>0 else 0
        var = (t - s*avg) / (n-1) if n>1 else 0
        if -0.0000001 < var and var < 0:
            var = 0
        std = sqrt(var)
        self.data[ruleset][measure]["avg"] = avg
        self.data[ruleset][measure]["var"] = var
        self.data[ruleset][measure]["std"] = std

    def run_initial_elections(self):
        self.base_allocations = []
        for r in range(self.num_rulesets):
            election = self.e_handler.elections[r]
            xtd_total_seats = add_totals(election.results)
            xtd_const_seats = add_totals(election.m_const_seats_alloc)
            xtd_adj_seats = matrix_subtraction(xtd_total_seats, xtd_const_seats)
            xtd_seat_shares = find_xtd_shares(xtd_total_seats)

            opt_rules = election.rules.generate_opt_ruleset()
            opt_election = voting.Election(opt_rules, election.m_votes)
            opt_results = opt_election.run()
            bi_seat_shares = self.calculate_bi_seat_shares(r, election, opt_results)
            xtd_bi_seat_shares = add_totals(bi_seat_shares)
            self.base_allocations.append({
                "xtd_const_seats": xtd_const_seats,
                "xtd_adj_seats": xtd_adj_seats,
                "xtd_total_seats": xtd_total_seats,
                "xtd_seat_shares": xtd_seat_shares,
                "xtd_bi_seat_shares": xtd_bi_seat_shares,
                "step_info": election.adj_seats_info,
            })

    def gen_votes(self):
        """
        Generate votes similar to given votes using the given
        generating method.
        """
        gen = GENERATING_METHODS[self.variate]
        while True:
            votes = gen(self.base_votes, self.stbl_param)
            yield votes

    def test_generated(self):
        """Analysis of generated votes."""
        var_beta_distr = []
        for c in range(1+self.num_constituencies):
            var_beta_distr.append([])
            for p in range(1+self.num_parties):
                for measure in VOTE_MEASURES.keys():
                    self.analyze_list(-1, measure, c, p)
                var_beta_distr[c].append(1/sqrt(self.stbl_param)
                                        *self.xtd_vote_shares[c][p]
                                        *(self.xtd_vote_shares[c][p]-1))
        sim_shares = self.list_data[-1]["sim_shares"]
        self.data[-1]["sim_shares"] = {
            "err_avg": error(sim_shares["avg"], self.xtd_vote_shares),
            "err_var": error(sim_shares["var"], var_beta_distr)
        }

    def collect_votes(self, votes):
        xtd_votes  = add_totals(votes)
        xtd_shares = find_xtd_shares(xtd_votes)
        for c in range(self.num_constituencies+1):
            for p in range(self.num_parties+1):
                self.aggregate_list(-1, "sim_votes", c, p, xtd_votes[c][p])
                self.aggregate_list(-1, "sim_shares", c, p, xtd_shares[c][p])

    def collect_measures(self, votes):
        self.collect_votes(votes)
        self.e_handler.set_votes(votes)
        for ruleset in range(self.num_rulesets):
            election = self.e_handler.elections[ruleset]
            self.collect_list_measures(ruleset, election)
            self.collect_general_measures(ruleset, election)

    def collect_list_measures(self, ruleset, election):
        const_seats_alloc = add_totals(election.m_const_seats_alloc)
        total_seats_alloc = add_totals(election.results)
        for c in range(1+election.num_constituencies):
            for p in range(1+self.num_parties):
                cs  = const_seats_alloc[c][p]
                ts  = total_seats_alloc[c][p]
                adj = ts - cs
                sh  = float(ts)/total_seats_alloc[c][-1]
                self.aggregate_list(ruleset, "const_seats", c, p, cs)
                self.aggregate_list(ruleset, "total_seats", c, p, ts)
                self.aggregate_list(ruleset, "adj_seats", c, p, adj)
                self.aggregate_list(ruleset, "seat_shares", c, p, sh)

    def collect_general_measures(self, ruleset, election):
        """Various tests to determine the quality of the given method."""
        self.aggregate_measure(ruleset, "adj_dev", election.adj_dev)
        opt_results = self.entropy(ruleset, election)
        self.deviation_measures(ruleset, election, opt_results)
        self.other_measures(ruleset, election, opt_results)

    def entropy(self, ruleset, election):
        opt_rules = election.rules.generate_opt_ruleset()
        opt_election = voting.Election(opt_rules, election.m_votes)
        opt_results = opt_election.run()
        entropy = election.entropy()
        entropy_deviation_ratio = 1 - exp(entropy - opt_election.entropy())
        self.aggregate_measure(ruleset, "entropy_ratio", entropy_deviation_ratio)
        self.aggregate_measure(ruleset, "entropy", entropy)
        return opt_results

    def deviation_measures(self, ruleset, election, opt_results):
        self.deviation(ruleset, "opt", None, election.results, opt_results)
        self.deviation(ruleset, "law", election.m_votes, election.results)
        self.deviation(ruleset, "ind_const", election.m_votes, election.results)
        self.deviation(ruleset, "all_adj", election.m_votes, election.results)
        v_results = [sum(x) for x in zip(*election.results)]
        self.deviation(ruleset, "one_const", [election.v_votes], [v_results])

    def other_measures(self, ruleset, election, opt_results):
        bi_seat_shares = self.calculate_bi_seat_shares(ruleset, election, opt_results)
        scale = 1.0/sum([
            1.0/s for c in bi_seat_shares for s in c if s!=0
        ])
        self.loosemore_hanby(ruleset, election, bi_seat_shares)
        self.sainte_lague(ruleset, election, bi_seat_shares, scale)
        self.dhondt_min(ruleset, election, bi_seat_shares)
        self.dhondt_sum(ruleset, election, bi_seat_shares, scale)

    def deviation(self, ruleset, option, votes, reference_results, results=None):
        if results == None:
            rules = self.e_rules[ruleset].generate_comparison_rules(option)
            results = voting.Election(rules, votes).run()
        deviation = dev(reference_results, results)
        self.aggregate_measure(ruleset, "dev_"+option, deviation)

    def calculate_bi_seat_shares(self, ruleset, election, opt_results):
        scalar = float(election.total_seats) / sum(sum(x) for x in election.m_votes)
        bi_seat_shares = scale_matrix(election.m_votes, scalar)
        seats_party_opt = [sum(x) for x in zip(*opt_results)]
        rein = 0
        error = 1
        if self.num_parties > 1 and election.num_constituencies > 1:
            while round(error, 5) != 0.0:
                error = 0
                if self.sim_rules["row_constraints"]:
                    for c in range(election.num_constituencies):
                        s = sum(bi_seat_shares[c])
                        if s != 0:
                            mult = float(election.v_desired_row_sums[c])/s
                            error += abs(1-mult)
                            mult += rein*(1-mult)
                            for p in range(self.num_parties):
                                bi_seat_shares[c][p] *= mult
                if self.sim_rules["col_constraints"]:
                    for p in range(self.num_parties):
                        s = sum([c[p] for c in bi_seat_shares])
                        if s != 0:
                            mult = float(seats_party_opt[p])/s
                            error += abs(1-mult)
                            mult += rein*(1-mult)
                            for c in range(election.num_constituencies):
                                bi_seat_shares[c][p] *= mult

        try:
            assert [sum(x) for x in zip(*bi_seat_shares)] == seats_party_opt
        except AssertionError:
            pass
        try:
            assert [sum(x) for x in bi_seat_shares] == election.v_desired_row_sums
        except AssertionError:
            pass

        return bi_seat_shares

    def loosemore_hanby(self, ruleset, election, bi_seat_shares):
        scale = 1.0/election.total_seats
        lh = sum([
            abs(bi_seat_shares[c][p]-election.results[c][p])
            for p in range(self.num_parties)
            for c in range(election.num_constituencies)
        ])
        lh *= scale
        self.aggregate_measure(ruleset, "loosemore_hanby", lh)

    def sainte_lague(self, ruleset, election, bi_seat_shares, scale):
        stl = sum([
            (bi_seat_shares[c][p]-election.results[c][p])**2/bi_seat_shares[c][p]
            for p in range(self.num_parties)
            for c in range(election.num_constituencies)
            if bi_seat_shares[c][p] != 0
        ])
        stl *= scale
        self.aggregate_measure(ruleset, "sainte_lague", stl)

    def dhondt_min(self, ruleset, election, bi_seat_shares):
        dh_min = min([
            bi_seat_shares[c][p]/float(election.results[c][p])
            for p in range(self.num_parties)
            for c in range(election.num_constituencies)
            if election.results[c][p] != 0
        ])
        self.aggregate_measure(ruleset, "dhondt_min", dh_min)

    def dhondt_sum(self, ruleset, election, bi_seat_shares, scale):
        dh_sum = sum([
            max(0, bi_seat_shares[c][p]-election.results[c][p])/bi_seat_shares[c][p]
            for p in range(self.num_parties)
            for c in range(election.num_constituencies)
            if bi_seat_shares[c][p] != 0
        ])
        dh_sum *= scale
        self.aggregate_measure(ruleset, "dhondt_sum", dh_sum)

    def analysis(self):
        """Calculate averages and variances of various quality measures."""
        for ruleset in range(self.num_rulesets):
            for measure in MEASURES.keys():
                self.analyze_measure(ruleset, measure)
            num_constituencies = len(self.e_rules[ruleset]["constituencies"])
            for c in range(1+num_constituencies):
                for p in range(1+self.num_parties):
                    for measure in LIST_MEASURES.keys():
                        self.analyze_list(ruleset, measure, c, p)
        self.analyze_measure(-1, "time")

    def simulate(self):
        """Simulate many elections."""
        gen = self.gen_votes()
        if self.num_total_simulations == 0:
            self.collect_measures(self.base_votes)
        for i in range(self.num_total_simulations):
            round_start = datetime.now()
            if self.terminate:
                break
            self.iteration = i + 1
            votes = next(gen)
            self.collect_measures(votes)
            round_end = datetime.now()
            self.iteration_time = round_end - round_start
            self.aggregate_measure(-1, "time", self.iteration_time.total_seconds())
        self.analysis()
        self.test_generated()


    def get_results_dict(self):
        self.analysis()
        return {
            "testnames": [rules["name"] for rules in self.e_rules],
            "methods": [rules["adjustment_method"] for rules in self.e_rules],
            "measures": MEASURES,
            "deviation_measures": DEVIATION_MEASURES,
            "standardized_measures": STANDARDIZED_MEASURES,
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
            "vote_data": self.list_data[-1],
            "time_data": self.data[-1]["time"]
        }

    def to_xlsx(self, filename):
        simulation_to_xlsx(self, filename)

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
