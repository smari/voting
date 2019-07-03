

from electionRules import ElectionRules
from voting import Election
from table_util import add_totals
from input_util import check_vote_table, check_rules
from excel_util import elections_to_xlsx

class ElectionHandler:
    """A handler for comparing electoral system results of a single election

    A class for managing comparison of results fom different electoral systems,
        on a common vote table.
    """
    def __init__(self, vote_table, election_rules_list):
        self.election_rules_list = check_rules(election_rules_list)
        self.vote_table = check_vote_table(vote_table)
        self.name = self.vote_table["name"]
        self.parties = self.vote_table["parties"]
        self.num_parties = len(self.parties)
        self.constituencies = self.vote_table["constituencies"]
        self.num_constituencies = len(self.constituencies)
        self.set_votes(self.vote_table["votes"])

    def set_votes(self, votes):
        assert len(votes) == self.num_constituencies, (
            "Vote_table does not match constituency list.")
        assert all(len(row) == self.num_parties for row in votes), (
            "Vote_table does not match party list.")

        self.votes = votes
        self.xtd_votes = add_totals(self.votes)

        self._setup_elections()

    def _setup_elections(self):
        self.elections = []
        for electoral_system in self.election_rules_list:
            rules = ElectionRules()
            rules.update(electoral_system)
            rules["parties"] = self.parties
            option = electoral_system["seat_spec_option"]
            if option == "defer":
                rules["constituencies"] = self.constituencies
                election = Election(rules, self.votes, self.name)
            elif option == "all_const":
                rules["constituencies"] = self.constituencies
                rules = rules.generate_ind_const_ruleset()
                election = Election(rules, self.votes, self.name)
            elif option == "all_adj":
                rules["constituencies"] = self.constituencies
                rules = rules.generate_all_adj_ruleset()
                election = Election(rules, self.votes, self.name)
            elif option == "one_const":
                rules = rules.generate_one_const_ruleset()
                total_votes = self.xtd_votes[-1][:-1]
                election = Election(rules, [total_votes], self.name)
            else:
                assert option == "custom", (
                    f"unexpected seat_spec_option encountered: {option}")
                rules["constituencies"] = []
                for const in self.constituencies:
                    match = const
                    for modified_const in electoral_system["constituencies"]:
                        if modified_const["name"] == const["name"]:
                            match = modified_const
                            break
                    rules["constituencies"].append(match)
                election = Election(rules, self.votes, self.name)
            self.elections.append(election)
        self.run_elections()

    def run_elections(self):
        for election in self.elections:
            election.run()

    def to_xlsx(self, filename):
        elections_to_xlsx(self.elections, filename)
