
def check_vote_table(vote_table):
    """Checks vote_table input, and translates empty cells to zeroes

    Raises:
        KeyError: If vote_table or constituencies are missing a component
        ValueError: If the dimensions of the table are inconsistent
            or not enough seats are specified
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
        raise ValueError("The vote_table does not match the constituency list.")
    for row in vote_table["votes"]:
        if not len(row) == num_parties:
            raise ValueError("The vote_table does not match the party list.")
        for p in range(len(row)):
            if not row[p]: row[p] = 0
            if type(row[p]) != int: raise TypeError("Votes must be numbers.")

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
