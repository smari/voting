import json

class Rules(dict):
    """A set of rules for an election or a simulation to follow."""

    def __init__(self):
        self.value_rules = {}
        self.range_rules = {}
        self.list_rules = []
        super(Rules, self).__init__()

    def __setitem__(self, key, value):
        if key in self.value_rules and value not in self.value_rules[key]:
            raise ValueError("Cannot set %s to '%s'. Allowed values: %s" %
                             (key, value, self.value_rules[key]))
        if key in self.range_rules and (value < self.range_rules[key][0] or
                                        value > self.range_rules[key][1]):
            raise ValueError("Cannot set %s to '%.02f'. Allowed values are \
between %.02f and %.02f" % (key, value, self.range_rules[key][0],
                            self.range_rules[key][1]))
        if key in self.list_rules and not isinstance(value, list):
            raise ValueError("Cannot set %s to '%s'. Must be a list." %
                             (key, value))

        super(Rules, self).__setitem__(key, value)

