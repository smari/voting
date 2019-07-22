
from distutils.util import strtobool

from dictionaries import SEAT_SPECIFICATION_OPTIONS


def check_input(data, sections):
    for section in sections:
        if section not in data or not data[section]:
            raise KeyError(f"Missing data ('{section}')")
    return data

def check_vote_table(vote_table):
    """Checks vote_table input, and translates empty cells to zeroes

    Raises:
        KeyError: If vote_table or constituencies are missing a component
        ValueError: If the dimensions of the table are inconsistent,
            negative values are supplied as vote counts,
            some constituency has no votes or seats specified,
            or constituency names are not unique
        TypeError: If vote or seat counts are not given as numbers
    """
    for info in [
        "name",
        "votes",
        "parties",
        "constituencies",
    ]:
        if info not in vote_table or not vote_table[info]:
            raise KeyError(f"Missing data ('vote_table.{info}')")

    num_parties = len(vote_table["parties"])
    num_constituencies = len(vote_table["constituencies"])

    if not len(vote_table["votes"]) == num_constituencies:
        raise ValueError("The vote table does not match the constituency list.")
    for row in vote_table["votes"]:
        if not len(row) == num_parties:
            raise ValueError("The vote table does not match the party list.")
        for p in range(len(row)):
            if not row[p]: row[p] = 0
            if type(row[p]) != int: raise TypeError("Votes must be numbers.")
            if row[p]<0: raise ValueError("Votes may not be negative.")
        if sum(row)==0: raise ValueError("Every constituency needs some votes.")

    for const in vote_table["constituencies"]:
        if "name" not in const or not const["name"]:
            raise KeyError(f"Missing data ('vote_table.constituencies[x].name')")
        name = const["name"]
        for info in ["num_const_seats", "num_adj_seats"]:
            if info not in const:
                raise KeyError(f"Missing data ('{info}' for {name})")
            if not const[info]: const[info] = 0
            if type(const[info]) != int:
                raise TypeError("Seat specifications must be numbers.")
        if const["num_const_seats"]+const["num_adj_seats"] <= 0:
            raise ValueError("Constituency seats and adjustment seats "
                             "must add to a nonzero number. "
                             f"This is not the case for {name}.")

    seen = set()
    for const in vote_table["constituencies"]:
        if const["name"] in seen:
            raise ValueError("Constituency names must be unique. "
                             f"{const['name']} is not.")
        seen.add(const["name"])

    return vote_table

def check_rules(electoral_systems):
    """Checks election rules constituency input, and translates empty cells to 0

    Raises:
        KeyError: If constituencies are missing a component
        TypeError: If seat counts are not given as numbers
        ValueError: If not enough seats are specified
    """
    if not electoral_systems:
        raise ValueError("Must have at least one electoral system.")
    for electoral_system in electoral_systems:
        # option = electoral_system["seat_spec_option"]
        # assert option in SEAT_SPECIFICATION_OPTIONS.keys(), (
        #     f"Unexpected seat specification option encountered: {option}.")
        # if option == "custom":
        # We only really need to check input if option is "custom",
        # because in case of the other options this won't be evaluated anyway,
        # except for option "one_const", and even then,
        # the frontend can't reach a state where that option would be corrupted.
        # But let's just check all, to be helpful also
        # in case POST data does not come from frontend but elsewhere.
        for const in electoral_system["constituencies"]:
            if "name" not in const or not const["name"]:
                #can never happen in case of input from frontend
                raise KeyError(f"Missing data ('constituencies[x].name' in "
                    f"electoral system {electoral_system['name']})")
            name = const["name"]
            for info in ["num_const_seats", "num_adj_seats"]:
                if info not in const:
                    raise KeyError(f"Missing data ('{info}' for {name} in "
                        f"electoral system {electoral_system['name']})")
                if not const[info]: const[info]=0
                if type(const[info]) != int:
                    raise TypeError("Seat specifications must be numbers.")
            if (const["num_const_seats"] + const["num_adj_seats"] <= 0):
                raise ValueError("Constituency seats and adjustment seats "
                     "must add to a nonzero number. "
                     f"This is not the case for {name} in "
                     f"electoral system {electoral_system['name']}.")
    return electoral_systems

def check_simulation_rules(sim_rules):
    """Checks simulation rules, and translates checkbox values to bool values

    Raises:
        KeyError: If simulation rules are missing a component
        ValueError: If stability parameter is too low
    """
    for key in ["simulation_count", "gen_method", "row_constraints", "col_constraints"]:
        if key not in sim_rules:
            raise KeyError(f"Missing data ('simulation_rules.{key}')")
    if sim_rules["gen_method"] == "beta":
        if "distribution_parameter" not in sim_rules:
            raise KeyError("Missing data ('simulation_rules.distribution_parameter')")
        stability_parameter = sim_rules["distribution_parameter"]
        if stability_parameter <= 1:
            raise ValueError("Stability parameter must be greater than 1.")
    for key in ["row_constraints", "col_constraints"]:
        sim_rules[key] = bool(strtobool(str(sim_rules[key])))
    return sim_rules
