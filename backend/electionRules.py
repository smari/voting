
import json
from copy import copy, deepcopy

from rules import Rules
from util import load_constituencies
from dictionaries import DIVIDER_RULES, QUOTA_RULES, RULE_NAMES, ADJUSTMENT_METHODS
from dictionaries import SEAT_SPECIFICATION_OPTIONS

class ElectionRules(Rules):
    """A set of rules for an election to follow."""

    def __init__(self):
        super(ElectionRules, self).__init__()
        self.value_rules = {
            "primary_divider": RULE_NAMES.keys(),
            "adj_determine_divider": RULE_NAMES.keys(),
            "adj_alloc_divider": DIVIDER_RULES.keys(),
            "adjustment_method": ADJUSTMENT_METHODS.keys(),
            "seat_spec_option": SEAT_SPECIFICATION_OPTIONS.keys(),
        }
        self.range_rules = {
            "adjustment_threshold": [0, 100],
            "constituency_threshold": [0, 100],
        }
        self.list_rules = [
            "constituencies", "parties"
        ]

        self["name"] = "My electoral system"

        # Election rules
        self["primary_divider"] = "dhondt"
        self["adj_determine_divider"] = "dhondt"
        self["adj_alloc_divider"] = "dhondt"
        self["adjustment_threshold"] = 5
        self["constituency_threshold"] = 0
        self["adjustment_method"] = "icelandic-law"
        self["seat_spec_option"] = "refer"
        self["constituencies"] = []
        self["parties"] = []

        # Display rules
        self["debug"] = False
        self["show_entropy"] = False
        self["output"] = "simple"

    def __setitem__(self, key, value):
        if key == "constituencies" and type(value) == str:
            value = load_constituencies(value)

        super(ElectionRules, self).__setitem__(key, value)

    def get_generator(self, div):
        """Fetch a generator from divider rules."""
        method = self[div]
        if method in DIVIDER_RULES.keys():
            return DIVIDER_RULES[method]
        elif method in QUOTA_RULES.keys():
            return QUOTA_RULES[method]
        else:
            raise ValueError("%s is not a known divider" % div)

    def get_type(self, rule):
        method = self[rule]
        if method in DIVIDER_RULES.keys():
            return "Division"
        elif method in QUOTA_RULES.keys():
            return "Quota"
        else:
            raise ValueError(f"{rule} is not a known rule")


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
        ref_rs["constituencies"] = deepcopy(self["constituencies"])
        for const in ref_rs["constituencies"]:
            const["num_const_seats"] += const["num_adj_seats"]
            const["num_adj_seats"] = 0
        return ref_rs

    def generate_one_const_ruleset(self):
        ref_rs = ElectionRules()
        ref_rs.update(self)
        ref_rs["constituencies"] = [{
            "name": "All",
            "num_const_seats": sum([const["num_const_seats"]
                for const in self["constituencies"]]),
            "num_adj_seats": sum([const["num_adj_seats"]
                for const in self["constituencies"]]),
        }]
        return ref_rs

    def generate_all_adj_ruleset(self):
        ref_rs = ElectionRules()
        ref_rs.update(self)
        ref_rs["constituencies"] = deepcopy(self["constituencies"])
        for const in ref_rs["constituencies"]:
            const["num_adj_seats"] += const["num_const_seats"]
            const["num_const_seats"] = 0
        return ref_rs
