#coding:utf-8
import random
from backports import csv
import sys #??????
from tabulate import tabulate
import io
import os
import openpyxl
import configparser
import codecs
from distutils.util import strtobool

#??????
def random_id(length=8):
    chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    s = "".join(random.sample(chars, length))
    return s


def read_csv(filename):
    with io.open(filename, mode="r", newline='', encoding='utf-8') as f:
        for row in csv.reader(f, skipinitialspace=True):
            yield [cell for cell in row]

def read_xlsx(filename):
    book = openpyxl.load_workbook(filename)
    sheet = book.active
    for row in sheet.rows:
        yield [cell.value for cell in row]

def load_constituencies(confile):
    """Load constituencies from a file."""
    if confile.endswith("csv"):
        reader = read_csv(confile)
    else:
        reader = read_xlsx(confile)
    cons = []
    for row in reader:
        try:
            assert(int(row[1]) + int(row[2]) > 0)
        except Exception as e:
            print(row[1:3])
            raise Exception("Error loading constituency file: "
                            "constituency seats and adjustment seats "
                            "must add to a nonzero number.")
        cons.append({
            "name": row[0],
            "num_const_seats": int(row[1]),
            "num_adj_seats": int(row[2])})
    return cons

def load_votes_from_stream(stream, filename):
    rd = []
    if filename.endswith(".csv"):
        if isinstance(stream, io.TextIOWrapper) and stream.encoding != 'utf-8':
            stream.reconfigure(encoding='utf-8')
        if isinstance(stream, io.BytesIO):
            stream = codecs.iterdecode(stream, 'utf-8')
        for row in csv.reader(stream, skipinitialspace=True):
            rd.append(row)
    elif filename.endswith(".xlsx"):
        if not hasattr(stream, "seekable") and hasattr(stream, "_file"):
            stream.seekable = stream._file.seekable  # TODO: Remove this monkeypatch once this issue has been resolved.
        book = openpyxl.load_workbook(stream)
        sheet = book.active
        for row in sheet.rows:
            rd.append([cell.value for cell in row])
    else:
        return None, None, None

    name_incl = rd[0][0].lower() != u"kjördæmi" if rd[0][0] else False
    const_seats_incl = rd[0][1].lower() == "cons"
    expected = 2 if const_seats_incl else 1
    adj_seats_incl = rd[0][expected].lower() == "adj"

    return parse_input(
        input=rd,
        name_included=name_incl,
        parties_included=True,
        const_included=True,
        const_seats_included=const_seats_incl,
        adj_seats_included=adj_seats_incl,
        filename=filename
    )

def parse_input(
    input,
    name_included,
    parties_included,
    const_included,
    const_seats_included,
    adj_seats_included,
    filename=''
):
    name_included = strtobool(str(name_included))
    parties_included = strtobool(str(parties_included))
    const_included = strtobool(str(const_included))
    const_seats_included = strtobool(str(const_seats_included))
    adj_seats_included = strtobool(str(adj_seats_included))

    res = {}
    start_row = 0
    if name_included or parties_included:
        start_row += 1
    start_col = 0
    if name_included or const_included:
        start_col += 1
    if const_seats_included:
        const_col = start_col
        start_col += 1
    if adj_seats_included:
        adj_col = start_col
        start_col += 1

    res["votes"] = [[parsint(v) for v in row[start_col:]]
                    for row in input[start_row:]]

    if parties_included:
        res["parties"] = input[0][start_col:]
        while res["parties"] and not res["parties"][-1]:
            res["parties"] = res["parties"][:-1]
        num_parties = len(res["parties"])
        res["votes"] = [row[:num_parties] for row in res["votes"]]
    else:
        num_parties = max(len(row) for row in res["votes"])
        res["parties"] = ['']*num_parties

    res["constituencies"] = [{
        "name": row[0] if const_included else '',
        "num_const_seats": parsint(row[const_col]) if const_seats_included else 0,
        "num_adj_seats": parsint(row[adj_col]) if adj_seats_included else 0,
    } for row in input[start_row:]]

    table_name = input[0][0] if name_included else ''
    res["name"] = determine_table_name(table_name,filename)

    return res

def parsint(value):
    return int(value) if value else 0

def determine_table_name(first,filename):
    return first if first else os.path.splitext(filename)[0]

def load_votes(votefile, consts):
    """Load votes from a file."""
    if votefile.endswith("csv"):
        reader = read_csv(votefile)
    else:
        reader = read_xlsx(votefile)
    parties = next(reader)[3:]
    votes = [[] for i in range(len(consts))]
    c_names = [x["name"] for x in consts]

    for row in reader:
        try:
            v = votes[c_names.index(row[0])]
        except:
            print(row)
            raise Exception("Constituency '%s' not found in constituency file"
                            % row[0])
        for x in row[3:]:
            try:
                r = float(x)
            except:
                r = 0
            v.append(r)

    return parties, votes

def print_table(data, header, labels, output, f_string=None):
    """
    Print 'data' in a table with 'header' and rows labelled with 'labels'.
    """
    if f_string:
        data = [[f_string.format(d) if d!=None else d for d in row] for row in data]
    data = [[labels[i]] + data[i] for i in range(len(data))]
    data = [[d if d != 0 and d != "0.0%" else None for d in row]
                for row in data]
    print(tabulate(data, header, output))

def print_steps_election(election):
    """Print detailed information about a single election."""
    rules = election.rules
    out = rules["output"]
    header = ["Constituency"]
    header.extend(rules["parties"])
    header.append("Total")
    if "constituencies" in rules:
        const_names = [c["name"] for c in rules["constituencies"]]
    else:
        const_names = rules["constituency_names"]
    const_names.append("Total")

    print("Votes")
    xtd_votes = add_totals(election.m_votes)
    print_table(xtd_votes, header, const_names, out)

    print("\nVote shares")
    xtd_shares = find_xtd_shares(xtd_votes)
    print_table(xtd_shares, header, const_names, out, "{:.1%}")

    print("\nConstituency seats")
    xtd_const_seats = add_totals(election.m_const_seats_alloc)
    print_table(xtd_const_seats, header, const_names, out)

    print("\nAdjustment seat apportionment")
    print("Threshold: {:.1%}".format(rules["adjustment_threshold"]*0.01))
    v_votes = election.v_votes
    v_votes.append(sum(election.v_votes))
    v_elim_votes = election.v_votes_eliminated
    v_elim_votes.append(sum(election.v_votes_eliminated))
    v_elim_shares = ["{:.1%}".format(v/v_elim_votes[-1])
                        for v in v_elim_votes]
    v_const_seats = election.v_const_seats_alloc
    v_const_seats.append(sum(election.v_const_seats_alloc))
    data = [v_votes, v_elim_votes, v_elim_shares, v_const_seats]
    labels = ["Total votes", "Votes above threshold",
              "Vote shares above threshold", "Constituency seats"]
    print_table(data, header[1:], labels, out)

    table = election.demonstration_table
    print("")
    print(tabulate(table["steps"], table["headers"], out))
    print("")

    xtd_total_seats = add_totals(election.results)
    print("\nAdjustment seats")
    xtd_adj_seats = matrix_subtraction(xtd_total_seats, xtd_const_seats)
    print_table(xtd_adj_seats, header, const_names, out)

    print("\nTotal seats")
    print_table(xtd_total_seats, header, const_names, out)

    print("\nSeat shares")
    xtd_shares = find_xtd_shares(xtd_total_seats)
    print_table(xtd_shares, header, const_names, out, "{:.1%}")

def pretty_print_election(election):
    """Print results of a single election."""
    rules = election.rules
    header = ["Constituency"]
    header.extend(rules["parties"])
    header.append("Total")
    if "constituencies" in rules:
        const_names = [c["name"] for c in rules["constituencies"]]
    else:
        const_names = rules["constituency_names"]
    const_names.append("Total")
    xtd_results = add_totals(election.results)
    print_table(xtd_results, header, const_names, rules["output"])

def sim_election_rules(rs, test_method):
    """Get preset election rules for simulation from file."""
    config = configparser.ConfigParser()
    config.read("../data/presets/methods.ini")

    if test_method in config:
        rs.update(config[test_method])
    else:
        raise ValueError("%s is not a known apportionment method"
                            % test_method)
    rs["adjustment_threshold"] = float(rs["adjustment_threshold"])

    return rs

def print_simulation(simulation):
    """Print detailed information about a simulation."""
    for r in range(len(simulation.e_rules)):
        rules = simulation.e_rules[r]
        out = rules["output"]
        print("==========================================")
        print("Adjustment method:", rules["adjustment_method"])
        print("==========================================\n")
        h = ["Constituency"]
        h.extend(rules["parties"]+["Total"])
        if "constituencies" in rules:
            const_names = [c["name"] for c in rules["constituencies"]]
        else:
            const_names = rules["constituency_names"]
        const_names.append("Total")

        print("Reference")

        print("\nVotes")
        print_table(simulation.xtd_votes, h, const_names, out)

        print("\nVote shares")
        print_table(simulation.xtd_vote_shares, h, const_names, out, "{:.1%}")

        print("\nConstituency seats")
        print_table(simulation.base_allocations[r]["xtd_const_seats"], h, const_names, out)

        print("\nAdjustment seats")
        print_table(simulation.base_allocations[r]["xtd_adj_seats"], h, const_names, out)

        print("\nTotal seats")
        print_table(simulation.base_allocations[r]["xtd_total_seats"], h, const_names, out)

        print("\nSeat shares")
        print_table(simulation.base_allocations[r]["xtd_seat_shares"], h, const_names, out, "{:.1%}")

        print("\nAverages from simulation")

        print("\nVotes")
        print_table(simulation.list_data[-1]["sim_votes"]["avg"], h, const_names, out)

        print("\nVote shares")
        print_table(simulation.list_data[-1]["sim_shares"]["avg"], h, const_names, out, "{:.1%}")

        print("\nConstituency seats")
        print_table(simulation.list_data[r]["const_seats"]["avg"], h, const_names, out)

        print("\nAdjustment seats")
        print_table(simulation.list_data[r]["adj_seats"]["avg"], h, const_names, out)

        print("\nTotal seats")
        print_table(simulation.list_data[r]["total_seats"]["avg"], h, const_names, out)

        print("\nSeat shares")
        print_table(simulation.list_data[r]["seat_shares"]["avg"], h, const_names, out, "{:.1%}")

        print("\nStandard deviations from simulation")

        print("\nVotes")
        print_table(simulation.list_data[-1]["sim_votes"]["std"], h, const_names, out, "{:.3f}")

        print("\nVote shares")
        print_table(simulation.list_data[-1]["sim_shares"]["std"], h, const_names, out, "{:.1%}")

        print("\nConstituency seats")
        print_table(simulation.list_data[r]["const_seats"]["std"], h, const_names, out, "{:.3f}")

        print("\nAdjustment seats")
        print_table(simulation.list_data[r]["adj_seats"]["std"], h, const_names, out, "{:.3f}")

        print("\nTotal seats")
        print_table(simulation.list_data[r]["total_seats"]["std"], h, const_names, out, "{:.3f}")

        print("\nSeat shares")
        print_table(simulation.list_data[r]["seat_shares"]["std"], h, const_names, out, "{:.1%}")

        #print("\nVotes added to change results")
        #print_table(simulation.votes_to_change, h[:-1], const_names[:-1], out)
