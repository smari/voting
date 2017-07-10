from voting import Election, SIMULATION_VARIATES
from rules import Rules

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
        self.election = Election(self.rules, votes)
        for j in self.rules["simulation_variate"]:
            self.variates.append(SIMULATION_VARIATES[j](self.election))

    def simulate(self, votes):
        """Simulate many elections."""

        for i in range(self.rules["simulation_count"]):
            for v in self.variates:
                v.step(i)

            election.run()

    def fetch_results(self):
        pass
