
import json

from rules import Rules
from util import load_constituencies
from dictionaries import DIVIDER_RULES, DIVIDER_RULE_NAMES
from dictionaries import ADJUSTMENT_METHODS, ADJUSTMENT_METHOD_NAMES

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
