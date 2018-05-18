# from voting import Election, SIMULATION_VARIATES
from rules import Rules
from math import sqrt
from random import betavariate

def mean(v):
    return sum(v)/len(v)

def var(v, mean):
    return sum([(i-mean)**2 for i in v])/(len(v)-1)

def beta_params(mean, rho):
    alpha = mean*(1/rho**2 - 1)
    beta = alpha*(1/mean - 1)
    return alpha, beta

def beta_distribution(m_votes, rho):
    m_out = []
    m_voteshares = []
    totals = [sum(c) for c in m_votes]
    
    for i in range(len(m_votes)):
        s = 0
        m_out.append([])
        m_voteshares.append([])
        for j in range(len(m_votes[i])):
            mean = m_votes[i][j]/totals[i]
            # stddev = sqrt(rho**2 * mean * (1-mean))
            alpha, beta = beta_params(mean, rho)
            mbar = betavariate(alpha, beta)
            m_voteshares[i].append(mbar)
            m_out[i].append(int(mbar*totals[i]))

    return m_out, m_voteshares

def testsim(m_votes, n=10000, rho=0.1):
    error = 0
    resultset = []
    print("Generating %d results" % n)
    for it in range(n):
        _, shares = beta_distribution(m_votes, rho)
        resultset.append(shares)

    print("Generation done.")

    for i in range(len(shares)):
        for j in range(len(shares[i])):
            sharesij = [resultset[k][i][j] for k in range(n)]
            mbar = mean(sharesij)
            variance = var(sharesij, mbar)
            rhobar = variance/(mbar*(1-mbar))
            error += (rho**2 - rhobar)**2
    print("Error estimation done.")

    return error




class SimulationRules(Rules):
    def __init__(self):
        super(SimulationRules, self).__init__()
        # Simulation rules
        self["simulate"] = False
        self["simulation_count"] = 100
        self["simulation_variate"] = "beta"


class Simulation:
    """Simulate a set of elections."""
    def __init__(self, rules, votes):
        self.rules = rules
        self.votes = votes
        self.variates = []
        self.election = 0 # Election(self.rules, votes)
        for j in self.rules["simulation_variate"]:
            self.variates.append(SIMULATION_VARIATES[j](self.election))

    def simulate(self, votes):
        """Simulate many elections."""

        for i in range(self.rules["simulation_count"]):
            for v in self.variates:
                v.step(i)

            pass # election.run()

    def fetch_results(self):
        pass
