
import json
from copy import copy

from rules import Rules
from util import load_constituencies
from dictionaries import DIVIDER_RULES
from dictionaries import ADJUSTMENT_METHODS

class ElectionRules(Rules):
    """A set of rules for an election to follow."""

    def __init__(self):
        super(ElectionRules, self).__init__()
        self.value_rules = {
            "primary_divider": DIVIDER_RULES.keys(),
            "adj_determine_divider": DIVIDER_RULES.keys(),
            "adj_alloc_divider": DIVIDER_RULES.keys(),
            "adjustment_method": ADJUSTMENT_METHODS.keys(),
        }
        self.range_rules = {
            "adjustment_threshold": [0, 100]
        }
        self.list_rules = [
            "constituency_seats", "constituency_adjustment_seats",
            "constituency_names", "parties"
        ]

        self["name"] = "My test"

        # Election rules
        self["primary_divider"] = "dhondt"
        self["adj_determine_divider"] = "dhondt"
        self["adj_alloc_divider"] = "dhondt"
        self["adjustment_threshold"] = 5
        self["adjustment_method"] = "icelandic-law"
        self["constituency_seats"] = []
        self["constituency_adjustment_seats"] = []
        self["constituency_names"] = []
        self["parties"] = []

        # Display rules
        self["debug"] = False
        self["show_entropy"] = False
        self["output"] = "simple"

    def __setitem__(self, key, value):
        if key == "constituencies":
            value = load_constituencies(value)
            self["constituency_names"] = [x["name"] for x in value]
            self["constituency_seats"] = [x["num_constituency_seats"]
                                          for x in value]
            self["constituency_adjustment_seats"] = [x["num_adjustment_seats"]
                                                     for x in value]

        super(ElectionRules, self).__setitem__(key, value)

    def get_generator(self, div):
        """Fetch a generator from divider rules."""
        method = self[div]
        if method in DIVIDER_RULES.keys():
            return DIVIDER_RULES[method]
        else:
            raise ValueError("%s is not a known divider" % div)



    def generate_comparison_rules(self, option="all"):
        if option == "opt":
            return self.generate_opt_ruleset()
        if option == "law":
            return self.generate_law_ruleset()
        if option == "ind_const":
            return self.generate_ind_const_ruleset()
        if option == "one_const":
            return self.generate_one_const_ruleset()
        if option == "all_adj":
            return self.generate_all_adj_ruleset()
        if option == "all":
            return {
                "opt":       self.generate_opt_ruleset(),
                "law":       self.generate_law_ruleset(),
                "ind_const": self.generate_ind_const_ruleset(),
                "one_const": self.generate_one_const_ruleset(),
                "all_adj":   self.generate_all_adj_ruleset()
            }
        return None

    def generate_opt_ruleset(self):
        ref_rs = ElectionRules()
        ref_rs.update(self)
        ref_rs["adjustment_method"] = "alternating-scaling"
        return ref_rs

    def generate_law_ruleset(self):
        ref_rs = ElectionRules()
        ref_rs.update(self)
        ref_rs["adjustment_method"] = "icelandic-law"
        ref_rs["primary_divider"] = "dhondt"
        ref_rs["adj_determine_divider"] = "dhondt"
        ref_rs["adj_alloc_divider"] = "dhondt"
        ref_rs["adjustment_threshold"] = 5
        return ref_rs

    def generate_ind_const_ruleset(self):
        ref_rs = ElectionRules()
        ref_rs.update(self)
        ref_rs["constituency_seats"] = copy(self["constituency_seats"])
        ref_rs["constituency_adjustment_seats"] = []
        for i in range(len(self["constituency_seats"])):
            ref_rs["constituency_seats"][i] += self["constituency_adjustment_seats"][i]
            ref_rs["constituency_adjustment_seats"].append(0)
        return ref_rs

    def generate_one_const_ruleset(self):
        ref_rs = ElectionRules()
        ref_rs.update(self)
        ref_rs["constituency_seats"] = [sum(self["constituency_seats"])]
        ref_rs["constituency_adjustment_seats"] = [sum(self["constituency_adjustment_seats"])]
        ref_rs["constituency_names"] = ["All"]
        return ref_rs

    def generate_all_adj_ruleset(self):
        ref_rs = ElectionRules()
        ref_rs.update(self)
        n = len(self["constituency_names"])
        ref_rs["constituency_seats"] = [0 for c in range(n)]
        ref_rs["constituency_adjustment_seats"] \
            = [self["constituency_seats"][c] \
               + self["constituency_adjustment_seats"][c]
               for c in range(n)]
        return ref_rs
