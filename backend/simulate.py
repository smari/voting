# from voting import Election, SIMULATION_VARIATES
from rules import Rules
from math import sqrt
from random import betavariate
from copy import copy

import voting
import io
import json
import configparser


def avg(v):
    return sum(v)/len(v)

def var(v, mean):
    return sum([(i-mean)**2 for i in v])/(len(v)-1)

def beta_params(mean, var_param):
    alpha = mean*(1/var_param**2 - 1)
    beta = alpha*(1/mean - 1)
    return alpha, beta

def beta_distribution(m_ref_votes, var_param):
    m_votes = []
    m_shares = []
    ref_totals = [sum(c) for c in m_ref_votes]
    
    for i in range(len(m_ref_votes)):
        s = 0
        m_votes.append([])
        m_shares.append([])
        for j in range(len(m_ref_votes[i])):
            mean_beta_distr = m_ref_votes[i][j]/ref_totals[i]
            if mean_beta_distr > 0:
                var_beta = var_param*mean_beta_distr*(1-mean_beta_distr)
                alpha, beta = beta_params(mean_beta_distr, var_param)
                share = betavariate(alpha, beta)
            else:
                share = 0
            m_shares[i].append(share)
            m_votes[i].append(int(share*ref_totals[i]))

    return m_votes, m_shares

def beta_gen(m_ref_votes, var_param):
    while True:
        yield beta_distribution(m_ref_votes, var_param)

GENERATING_METHODS = {
    "beta": beta_gen
}

def error(avg, ref):
    """
    Compare average of generated votes to reference votes to test the
    quality of the simulation.
    """
    num_consts = len(avg)
    num_parties = len(avg[0])
    s = 0
    for i in range(num_consts):
        for j in range(num_parties):
            if type(ref) is list:
                s += abs(avg[i][j] - ref[i][j])
            else:
                s += abs(avg[i][j] - ref)
    return s/(num_consts*num_parties)

def dev(results, ref):
    """Calculate seat deviation of results compared to reference results."""
    d = 0
    for i in range(len(results)):
        for j in range(len(results[i])):
            d += abs(results[i][j] - ref[i][j])
    return d


class SimulationRules(Rules):
    def __init__(self):
        super(SimulationRules, self).__init__()
        # Simulation rules
        self["simulate"] = False
        self["simulation_count"] = 10000
        self["simulation_variate"] = "beta"


class Simulation:
    """Simulate a set of elections."""
    def __init__(self, rules, election, var_param):
        self.rules = rules
        self.ref_votes = election.m_votes
        self.ref_shares = [[v/sum(c) for v in c] for c in self.ref_votes]
        self.variate = self.rules["simulation_variate"]
        self.election = election
        self.var_param = var_param
        self.results = []

    def gen_votes(self):
        """
        Generate votes similar to given votes using the given generating
        method.
        """
        self.simul_votes = []
        self.simul_shares = []
        gen = GENERATING_METHODS[self.variate]
        while True:
            votes, shares = next(gen(self.ref_votes, self.var_param))
            self.simul_votes.append(votes)
            self.simul_shares.append(shares)
            yield votes, shares

    def test_generated(self):
        """Analysis of generated votes."""
        avg_simul_shares = []
        var_simul_shares = []
        var_beta_distr = []

        for i in range(len(self.simul_shares[0])):
            avg_simul_shares.append([])
            var_simul_shares.append([])
            var_beta_distr.append([])
            for j in range(len(self.simul_shares[0][i])):
                shares_ij = [self.simul_shares[k][i][j] 
                            for k in range(self.rules["simulation_count"])]
                average = avg(shares_ij)
                variance = var(shares_ij, average)
                avg_simul_shares[i].append(average)
                var_simul_shares[i].append(variance)

                var_beta_distr[i].append(self.var_param
                                        *self.ref_shares[i][j]
                                        *(self.ref_shares[i][j]-1))


        self.avg_simul_shares = avg_simul_shares
        self.var_simul_shares = var_simul_shares
        self.error_avg_simul_shares = error(avg_simul_shares, self.ref_shares)
        self.error_var_simul_shares = error(var_simul_shares, var_beta_distr)


    def method_analysis(self, ref_rules):
        """Various tests to determine the quality of the given method."""
        n = self.rules["simulation_count"]
        opt_rules = ref_rules["opt"]
        ind_const_rules = ref_rules["ind_const"]
        one_country_rules = ref_rules["one_country"]
        tot_eq_one_country_rules = ref_rules["tot_eq_one_country"]
        self.entropy_ratio = []
        self.dev_opt = []
        self.dev_ind_const = []
        self.dev_one_country = []
        self.dev_tot_eq_one_country = []
        for i in range(n):
            votes = self.simul_votes[i]
            results = self.results[i]
            entropy = self.entropy[i]
            opt_election = voting.Election(opt_rules, votes)
            opt_results = opt_election.run()
            opt_entropy = opt_election.entropy()
            entropy_ratio = entropy/opt_entropy
            self.entropy_ratio.append(entropy_ratio)
            dev_opt = dev(results, opt_results)
            self.dev_opt.append(dev_opt)
            ind_const_election = voting.Election(ind_const_rules, votes)
            ind_const_results = ind_const_election.run()
            dev_ind_const = dev(results, ind_const_results)
            self.dev_ind_const.append(dev_ind_const)
            v_votes = [[sum([c[p] for c in votes]) for p in range(len(votes[0]))]]
            one_country_election = voting.Election(one_country_rules, v_votes)
            one_country_results = one_country_election.run()
            v_results = [[sum([c[p] for c in results]) for p in range(len(results[0]))]]
            dev_one_country = dev(v_results, one_country_results)
            self.dev_one_country.append(dev_one_country)
            tot_eq_one_country_election = voting.Election(tot_eq_one_country_rules, v_votes)
            tot_eq_one_country_results = tot_eq_one_country_election.run()
            dev_tot_eq_one_country = dev(v_results, tot_eq_one_country_results)
            self.dev_tot_eq_one_country.append(dev_tot_eq_one_country)

        self.avg_entropy = avg(self.entropy)
        self.avg_entropy_ratio = avg(self.entropy_ratio)
        self.avg_dev_opt = avg(self.dev_opt)
        self.avg_dev_ind_const = avg(self.dev_ind_const)
        self.avg_dev_one_country = avg(self.dev_one_country)
        self.avg_dev_tot_eq_one_country = avg(self.dev_tot_eq_one_country)
        print("Average entropy:")
        print(self.avg_entropy)
        print("Average entropy ratio:")
        print(self.avg_entropy_ratio)
        print("Average dev_opt:")
        print(self.avg_dev_opt)
        print("Average dev_ind_const:")
        print(self.avg_dev_ind_const)
        print("Average dev_one_country:")
        print(self.avg_dev_one_country)
        print("Average dev_tot_eq_one_country:")
        print(self.avg_dev_tot_eq_one_country)

    def simulate(self, e_rules, test_method):
        """Simulate many elections."""
        n = self.rules["simulation_count"]
        gen = self.gen_votes()
        self.entropy = []
        for i in range(n):
            votes, shares = next(gen)
            election = voting.Election(e_rules, votes)
            results = election.run()
            entropy = election.entropy()
            self.entropy.append(entropy)
            self.results.append(results)

        e_rules, ref_rules = sim_election_rules(e_rules, test_method)
        self.method_analysis(ref_rules)



    def fetch_results(self):
        pass

   # def simulate(self, election_rules):
        """Simulate many elections."""
"""
        n = self.rules["simulation_count"]
        gen = self.gen_votes()
        for i in range(n):
            votes, shares = next(gen)
            self.results.append([])
            for j in range(len(election_rules)):
              election = voting.Election(election_rules[j], votes)
              results = election.run()
              self.results[i].append(results)
"""

def sim_election_rules(rs, test_method):
    config = configparser.ConfigParser()
    config.read("methods.ini")

    opt_rs = voting.ElectionRules()
    ind_const_rs = voting.ElectionRules()
    one_country_rs = voting.ElectionRules()
    tot_eq_one_country_rs = voting.ElectionRules()

    if rules in config:
        rs.update(config[test_method])
    else:
        raise ValueError("%s is not a known apportionment method" % rules)
    rs["adjustment_threshold"] = float(rs["adjustment_threshold"])
    opt_rs.update(rs)
    opt_rs["adjustment_method"] = "alternating-scaling"
    ind_const_rs.update(rs)
    ind_const_rs["constituency_seats"] = copy(rs["constituency_seats"])
    ind_const_rs["constituency_adjustment_seats"] = []
    for i in range(len(rs["constituency_seats"])):
        ind_const_rs["constituency_seats"][i] += rs["constituency_adjustment_seats"][i]
        ind_const_rs["constituency_adjustment_seats"].append(0)
    one_country_rs.update(rs)
    one_country_rs["constituency_seats"] = [sum(rs["constituency_seats"])]
    one_country_rs["constituency_adjustment_seats"] = [sum(rs["constituency_adjustment_seats"])]
    one_country_rs["constituency_names"] = ["All"]
    tot_eq_one_country_rs.update(one_country_rs)
    tot_eq_one_country_rs["constituency_seats"] = [0]
    tot_eq_one_country_rs["constituency_adjustment_seats"] = [one_country_rs["constituency_seats"][0]
                        + one_country_rs["constituency_adjustment_seats"][0]]

    ref = {"opt": opt_rs,
            "ind_const": ind_const_rs,
            "one_country": one_country_rs, 
            "tot_eq_one_country": tot_eq_one_country_rs}

    return rs, ref

"""
def sim_election_rules(rs, rules):
    
    Get rules for apportionment method to test and construct reference rules
    for analysis of the method.
    
    with open(rules, "r") as read_file:
        rules = json.load(read_file)
    if type(rules) != dict:
        return {"error": "Incorrect rule format."}

    opt_rs = voting.ElectionRules()
    ind_const_rs = voting.ElectionRules()
    one_country_rs = voting.ElectionRules()
    tot_eq_one_country_rs = voting.ElectionRules()

    rs.update(rules["election_rules"])
    opt_rs.update(rs)
    opt_rs["adjustment_method"] = "alternating-scaling"
    ind_const_rs.update(rs)
    ind_const_rs["constituency_seats"] = copy(rs["constituency_seats"])
    ind_const_rs["constituency_adjustment_seats"] = []
    for i in range(len(rs["constituency_seats"])):
        ind_const_rs["constituency_seats"][i] += rs["constituency_adjustment_seats"][i]
        ind_const_rs["constituency_adjustment_seats"].append(0)
    one_country_rs.update(rs)
    one_country_rs["constituency_seats"] = [sum(rs["constituency_seats"])]
    one_country_rs["constituency_adjustment_seats"] = [sum(rs["constituency_adjustment_seats"])]
    one_country_rs["constituency_names"] = ["All"]
    tot_eq_one_country_rs.update(one_country_rs)
    tot_eq_one_country_rs["constituency_seats"] = [0]
    tot_eq_one_country_rs["constituency_adjustment_seats"] = [one_country_rs["constituency_seats"][0]
                        + one_country_rs["constituency_adjustment_seats"][0]]

    ref = {"opt": opt_rs,
            "ind_const": ind_const_rs,
            "one_country": one_country_rs, 
            "tot_eq_one_country": tot_eq_one_country_rs}

    return rs, ref
"""
