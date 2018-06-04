# from voting import Election, SIMULATION_VARIATES
from rules import Rules
from math import sqrt
from random import betavariate

import voting


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
        self.simul_votes = []
        self.simul_shares = []
        gen = GENERATING_METHODS[self.variate]
        while True:
            votes, shares = next(gen(self.ref_votes, self.var_param))
            self.simul_votes.append(votes)
            self.simul_shares.append(shares)
            yield votes, shares

    def test_generated(self):
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

    def simulate(self, election_rules):
        """Simulate many elections."""

        gen = self.gen_votes()
        for i in range(self.rules["simulation_count"]):
            votes, shares = next(gen)
            self.results.append([])
            for j in range(len(election_rules)):
              election = voting.Election(election_rules[j], votes)
              self.results[i].append(election.run())

    def fetch_results(self):
        pass
