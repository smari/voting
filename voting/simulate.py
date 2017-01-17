from voting import Election

class Simulation:
    """Simulate a set of elections."""
    def __init__(self, rules):
        self.rules = rules

    def simulate(self, votes):
        """Simulate many elections."""

        for i in range(self.rules["simulation_count"]):
            election = Election(self.rules, votes)
            election.run()

    def fetch_results(self):
        pass
