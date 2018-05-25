# from voting import Election, SIMULATION_VARIATES
from rules import Rules
from math import sqrt
from random import betavariate

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
            var_beta_distr = var_param*mean_beta_distr*(mean_beta_distr-1)
            alpha, beta = beta_params(mean_beta_distr, var_param)
            share = betavariate(alpha, beta)
            m_shares[i].append(share)
            m_votes[i].append(int(share*ref_totals[i]))

    return m_votes, m_shares

def beta_gen(m_ref_votes, var_param):
    while True:
        yield beta_distribution(m_ref_votes, var_param)

GENERATING_METHODS = {
    "beta": beta_gen
}

"""
def testsim(m_ref_votes, n=10000, rho=0.1):
    error = 0
    resultset = []
    print("Generating %d results" % n)
    for it in range(n):
        _, shares = beta_distribution(m_ref_votes, rho)
        resultset.append(shares)

    print("Generation done.")

    for i in range(len(shares)):
        for j in range(len(shares[i])):
            sharesij = [resultset[k][i][j] for k in range(n)]
            mbar = avg(sharesij)
            variance = var(sharesij, mbar)
            rhobar = variance/(mbar*(1-mbar))
            error += (rho**2 - rhobar)**2
    print("Error estimation done.")

    return error
"""

def error(avg, ref):
    num_consts = len(avg)
    num_parties = len(avg[0])
    s = 0
    for i in range(num_consts):
        for j in range(num_parties):
            if type(ref) is list:
                s += abs(avg[i][j] - ref[i][j])
            else:
                s += abs(avg[i][j] -ref)
    return s/(num_consts*num_parties)

def sim(election, method, n=10000, var_param=0.1):
    ref_votes = election.m_votes
    ref_shares = [[c[j]/sum(c) for j in range(len(c))] for c in ref_votes]
    simul_votes = []
    simul_shares = []
    gen = GENERATING_METHODS[method]
    for k in range(n):
        votes, shares = next(gen(ref_votes, var_param))
        simul_votes.append(votes)
        simul_shares.append(shares)

    avg_simul_shares = []
    var_simul_shares = []
    avg_var_params = []

    for i in range(len(simul_shares[0])):
        avg_simul_shares.append([])
        var_simul_shares.append([])
        avg_var_params.append([])
        for j in range(len(simul_shares[0][i])):
            shares_ij = [simul_shares[k][i][j] for k in range(n)]
            average = avg(shares_ij)
            variance = var(shares_ij, average)
            avg_simul_shares[i].append(average)
            var_simul_shares[i].append(variance)
            avg_var_params[i].append(variance/(average*(1-average)))

    error_avg_simul_shares = error(avg_simul_shares, ref_shares)
    #error_var_simul_shares = error(var_simul_shares, var_beta_distr)
    error_avg_var_param = error(avg_var_params, var_param)

    return simul_votes, simul_shares





class SimulationRules(Rules):
    def __init__(self):
        super(SimulationRules, self).__init__()
        # Simulation rules
        self["simulate"] = False
        self["simulation_count"] = 100
        self["simulation_variate"] = "beta"


class Simulation:
    """Simulate a set of elections."""
    def __init__(self, rules, election, var_param):
        self.rules = rules
        self.ref_votes = election.m_votes
        self.ref_shares = [[v/sum(c) for v in c] for c in self.ref_votes]
        self.variate = self.rules["simulation_variate"]
        # self.election = election
        self.var_param = var_param

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
        avg_var_params = []
        var_beta_distr = []

        for i in range(len(self.simul_shares[0])):
            avg_simul_shares.append([])
            var_simul_shares.append([])
            avg_var_params.append([])
            var_beta_distr.append([])
            for j in range(len(self.simul_shares[0][i])):
                shares_ij = [self.simul_shares[k][i][j] for k in range(self.rules["simulation_count"])]
                average = avg(shares_ij)
                variance = var(shares_ij, average)
                avg_simul_shares[i].append(average)
                var_simul_shares[i].append(variance)
                avg_var_params[i].append(variance/(average*(1-average)))

                var_beta_distr[i].append(self.var_param*self.ref_shares[i][j]*(self.ref_shares[i][j]-1))


        self.avg_simul_shares = avg_simul_shares
        self.var_simul_shares = var_simul_shares
        self.avg_var_params = avg_var_params
        self.error_avg_simul_shares = error(avg_simul_shares, self.ref_shares)
        self.error_var_simul_shares = error(var_simul_shares, var_beta_distr)
        self.error_avg_var_param = error(avg_var_params, self.var_param)
        print("Errors:")
        print(self.error_avg_simul_shares)
        print(self.error_var_simul_shares)
        print(self.error_avg_var_param)

    def simulate(self):
        """Simulate many elections."""

        gen = self.gen_votes()
        for i in range(self.rules["simulation_count"]):
            results = next(gen)
            # for r in e_rules:
            #   e = Election(r, results)
            #   e.run()

        print("Simulation done.")
        self.test_generated()


    def fetch_results(self):
        pass
