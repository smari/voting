#coding:utf-8
import random
from backports import csv
from math import log, sqrt
import sys #??????
from tabulate import tabulate
import io
import xlsxwriter
import openpyxl
from copy import deepcopy, copy
import configparser
import codecs

from methods import var_alt_scal, alternating_scaling, icelandic_law
from methods import monge, nearest_neighbor, relative_superiority
from methods import norwegian_law, norwegian_icelandic
from methods import opt_entropy, switching
from methods import pure_vote_ratios

#??????
def random_id(length=8):
    chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz'
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
            assert(int(row[1]) + int(row[2]) >= 0)
        except Exception as e:
            print(row[1:3])
            raise Exception("Error loading constituency file: "
                            "constituency seats and adjustment seats "
                            "must add to a nonzero number.")
        cons.append({
            "name": row[0],
            "num_constituency_seats": int(row[1]),
            "num_adjustment_seats": int(row[2])})
    return cons

def load_votes_from_stream(stream, filename):
    rd = []
    print("Stream:", stream)
    print("Filename:", filename)
    if filename.endswith(".csv"):
        for row in csv.reader(codecs.iterdecode(stream, 'utf-8'), skipinitialspace=True):
            rd.append(row)
    elif filename.endswith(".xlsx"):
        book = openpyxl.load_workbook(stream)
        sheet = book.active
        for row in sheet.rows:
            rd.append([cell.value for cell in row])
    else:
        return None, None, None

    print(tabulate(rd))

    parties = rd[0][1:]
    consts = [row[0] for row in rd[1:]]
    votes = [row[1:] for row in rd[1:]]

    return parties, consts, votes


def load_votes(votefile, consts):
    """Load votes from a file."""
    if votefile.endswith("csv"):
        reader = read_csv(votefile)
    else:
        reader = read_xlsx(votefile)
    parties = next(reader)[1:]
    votes = [[] for i in range(len(consts))]
    c_names = [x["name"] for x in consts]

    for row in reader:
        try:
            v = votes[c_names.index(row[0])]
        except:
            print(row)
            raise Exception("Constituency '%s' not found in constituency file"
                            % row[0])
        for x in row[1:]:
            try:
                r = float(x)
            except:
                r = 0
            v.append(r)

    return parties, votes

def add_totals(m):
    """Add sums of rows and columns to a table."""
    nm = deepcopy(m)
    for i in range(len(m)):
        nm[i].append(sum(m[i]))
    totals = [sum(x) for x in zip(*nm)]
    nm.append(totals)
    return nm

def print_table(data, header, labels, output):
    """
    Print 'data' in a table with 'header' and rows labelled with 'labels'.
    """
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
    votes = add_totals(election.m_votes)
    print_table(votes, header, const_names, out)

    print("\nVote shares")
    shares = [["{:.1%}".format(v/c[-1]) for v in c[:-1]]
                for c in votes]
    print_table(shares, header, const_names, out)

    print("\nConstituency seats")
    const_seats = add_totals(election.m_const_seats_alloc)
    print_table(const_seats, header, const_names, out)

    print("\nAdjustment seat apportionment")
    print("Threshold: {:.1%}".format(rules["adjustment_threshold"]))
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

    method = ADJUSTMENT_METHODS[rules["adjustment_method"]]
    try:
        h, data = method.print_seats(rules, election.adj_seats_info)
        print("")
        print(tabulate(data, h, out))
        print("")
    except AttributeError:
        pass

    total_seats = add_totals(election.results)
    print("\nAdjustment seats")
    adj_seats = [[total_seats[c][p]-const_seats[c][p]
                    for p in range(len(total_seats[c]))]
                    for c in range(len(total_seats))]
    print_table(adj_seats, header, const_names, out)

    print("\nTotal seats")
    print_table(total_seats, header, const_names, out)

    print("\nSeat shares")
    shares = [["{:.1%}".format(float(s)/c[-1]) if s != 0 else None for s in c[:-1]]
                for c in total_seats]
    print_table(shares, header, const_names, out)

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
    results = add_totals(election.results)
    print_table(results, header, const_names, rules["output"])

def entropy(votes, allocations, divisor_gen):
    """
    Calculate entropy of the election, taking into account votes and
     allocations.
     $\\sum_i \\sum_j \\sum_k \\log{v_{ij}/d_k}$, more or less.
    """
    assert(type(votes) == list)
    assert(all(type(v) == list for v in votes))
    assert(type(allocations) == list)
    assert(all(type(a) == list for a in allocations))

    e = 0
    for c in range(len(votes)):
        divisor_gens = [divisor_gen() for x in range(len(votes[c]))]
        for p in range(len(votes[c])):
            for k in range(allocations[c][p]):
                dk = next(divisor_gens[p])
                e += log(votes[c][p]/dk)
    return e

def election_to_xlsx(election, filename):
    """Write detailed information about a single election to an xlsx file."""
    if "constituencies" in election.rules:
        const_names = [c["name"] for c in election.rules["constituencies"]]
    else:
        const_names = election.rules["constituency_names"]
    const_names.append("Total")
    parties = election.rules["parties"] + ["Total"]
    votes = add_totals(election.m_votes)
    shares = [["{:.1%}".format(v/c[-1]) if v != 0 else None for v in c[:-1]]
                for c in votes]
    const_seats = add_totals(election.m_const_seats_alloc)
    total_seats = add_totals(election.results)
    adj_seats = [[total_seats[c][p]-const_seats[c][p]
                    for p in range(len(total_seats[c]))]
                    for c in range(len(total_seats))]
    seat_shares = [["{:.1%}".format(s/c[-1]) for s in c[:-1]]
                    for c in total_seats]

    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    cell_format = workbook.add_format()
    cell_format.set_align('right')
    h_format = workbook.add_format()
    h_format.set_align('center')
    h_format.set_bold()
    h_format.set_font_size(14)
    worksheet.set_column('B:B', 20)
    worksheet.merge_range(4, 2, 4, 1+len(parties), "Votes",
                                h_format)
    worksheet.write('B6', 'Constituency', cell_format)
    worksheet.write_row(5, 2, parties, cell_format)
    row = 5
    worksheet.write_column(6, 1, const_names, cell_format)
    for c in range(len(votes)):
        row += 1
        for p in range(len(votes[c])):
            if votes[c][p] != 0:
                worksheet.write(row, p+2, votes[c][p], cell_format)
    row += 2
    worksheet.merge_range(row, 2, row, 1+len(parties), "Vote shares",
                                h_format)
    row += 1
    worksheet.write(row, 1, 'Constituency', cell_format)
    worksheet.write_row(row, 2, parties[:-1], cell_format)
    worksheet.write_column(row+1, 1, const_names, cell_format)
    for c in range(len(shares)):
        row += 1
        worksheet.write_row(row, 2, shares[c], cell_format)
    row += 2
    worksheet.merge_range(row, 2, row, 1+len(parties), "Constituency seats",
                                h_format)
    row += 1
    worksheet.write(row, 1, 'Constituency', cell_format)
    worksheet.write_row(row, 2, parties, cell_format)
    worksheet.write_column(row+1, 1, const_names, cell_format)
    for c in range(len(const_seats)):
        row += 1
        for p in range(len(const_seats[c])):
            if const_seats[c][p] != 0:
                worksheet.write(row, p+2, const_seats[c][p], cell_format)
    row += 2
    worksheet.merge_range(row, 2, row, 6, "Adjustment seat apportionment",
                                h_format)
    worksheet.merge_range(row, 7, row, 8, "Threshold", h_format)
    worksheet.write(row, 9,
                    "{:.1%}".format(election.rules["adjustment_threshold"]),
                    cell_format)
    row += 1
    v_votes = votes[-1]
    v_elim_votes = election.v_votes_eliminated
    worksheet.write(row, 1, 'Party', cell_format)
    worksheet.write_row(row, 2, parties, cell_format)
    row += 1
    worksheet.write(row, 1, 'Total votes', cell_format)
    worksheet.write_row(row, 2, v_votes, cell_format)
    row += 1
    worksheet.write(row, 1, 'Votes above threshold', cell_format)
    for p in range(len(v_elim_votes)):
        if v_elim_votes[p] != 0:
            worksheet.write(row, p+2, v_elim_votes[p], cell_format)
    row += 1
    worksheet.write(row, 1, 'Vote shares above threshold', cell_format)
    for p in range(len(v_elim_votes)):
        if v_elim_votes[p] != 0:
            share = "{:.1%}".format(v_elim_votes[p]/sum(v_elim_votes[:-1]))
            worksheet.write(row, p+2, share, cell_format)
    row += 1
    v_elim_seats = []
    for p in range(len(v_elim_votes)-1):
        if v_elim_votes[p] != 0:
            v_elim_seats.append(election.v_const_seats_alloc[p])
        else:
            v_elim_seats.append(0)
    v_elim_seats.append(sum(v_elim_seats))
    worksheet.write(row, 1, 'Constituency seats', cell_format)
    for p in range(len(v_elim_seats)):
        if v_elim_seats[p] != 0:
            worksheet.write(row, p+2, v_elim_seats[p], cell_format)
    row += 2
    method = ADJUSTMENT_METHODS[election.rules["adjustment_method"]]
    try:
        h, data = method.print_seats(election.rules, election.adj_seats_info)
        worksheet.write_row(row, 1, h, cell_format)
        for i in range(len(data)):
            row += 1
            worksheet.write_row(row, 1, data[i], cell_format)
    except AttributeError:
        pass
    row += 2
    worksheet.merge_range(row, 2, row, 1+len(parties), "Adjustment seats",
                                h_format)
    row += 1
    worksheet.write(row, 1, 'Constituency', cell_format)
    worksheet.write_row(row, 2, parties, cell_format)
    worksheet.write_column(row+1, 1, const_names, cell_format)
    for c in range(len(adj_seats)):
        row += 1
        for p in range(len(adj_seats[c])):
            if adj_seats[c][p] != 0:
                worksheet.write(row, p+2, adj_seats[c][p], cell_format)
    row += 2
    worksheet.merge_range(row, 2, row, 1+len(parties), "Total seats",
                                h_format)
    row += 1
    worksheet.write(row, 1, 'Constituency', cell_format)
    worksheet.write_row(row, 2, parties, cell_format)
    worksheet.write_column(row+1, 1, const_names, cell_format)
    for c in range(len(total_seats)):
        row += 1
        for p in range(len(total_seats[c])):
            if total_seats[c][p] != 0:
                worksheet.write(row, p+2, total_seats[c][p], cell_format)
    row += 2
    worksheet.merge_range(row, 2, row, 1+len(parties), "Seat shares",
                                h_format)
    row += 1
    worksheet.write(row, 1, 'Constituency', cell_format)
    worksheet.write_row(row, 2, parties[:-1], cell_format)
    worksheet.write_column(row+1, 1, const_names, cell_format)
    for c in range(len(seat_shares)):
        row += 1
        for p in range(len(seat_shares[c])):
            if total_seats[c][p] != 0:
                worksheet.write(row, p+2, seat_shares[c][p], cell_format)
    row += 2
    worksheet.write(row, 1, 'Entropy:', h_format)
    worksheet.write(row, 2, election.entropy(), cell_format)

    workbook.close()

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
        votes = simulation.base_votes
        h = ["Constituency"]
        h.extend(rules["parties"]+["Total"])
        if "constituencies" in rules:
            const_names = [c["name"] for c in rules["constituencies"]]
        else:
            const_names = rules["constituency_names"]
        const_names.append("Total")

        print("Reference")

        print("\nVotes")
        xtd_votes = add_totals(votes)
        print_table(xtd_votes, h, const_names, out)

        print("\nVote shares")
        shares = [["{:.1%}".format(s) for s in c[:-1]]
                    for c in simulation.vote_shares]
        print_table(shares, h[:-1], const_names, out)

        print("\nConstituency seats")
        print_table(simulation.base_allocations[r]["xtd_const_seats"], h, const_names, out)

        print("\nAdjustment seats")
        print_table(simulation.base_allocations[r]["xtd_adj_seats"], h, const_names, out)

        print("\nTotal seats")
        print_table(simulation.base_allocations[r]["xtd_total_seats"], h, const_names, out)

        print("\nSeat shares")
        shares = [["{:.1%}".format(s) for s in c[:-1]]
                    for c in simulation.base_allocations[r]["seat_shares"]]
        print_table(shares, h[:-1], const_names, out)

        print("\nAverages from simulation")

        print("\nVotes")
        print_table(simulation.list_data[-1]["sim_votes"]["avg"], h, const_names, out)

        print("\nVote shares")
        shares = [["{:.1%}".format(s) for s in c[:-1]]
                    for c in simulation.list_data[-1]["sim_shares"]["avg"]]
        print_table(shares, h[:-1], const_names, out)

        print("\nConstituency seats")
        print_table(simulation.list_data[r]["const_seats"]["avg"], h, const_names, out)

        print("\nAdjustment seats")
        print_table(simulation.list_data[r]["adj_seats"]["avg"], h, const_names, out)

        print("\nTotal seats")
        print_table(simulation.list_data[r]["total_seats"]["avg"], h, const_names, out)

        print("\nSeat shares")
        shares = [["{:.1%}".format(s) for s in c[:-1]]
                    for c in simulation.list_data[r]["seat_shares"]["avg"]]
        print_table(shares, h[:-1], const_names, out)

        print("\nStandard deviations from simulation")

        print("\nVotes")
        sdev_votes = [[round(sqrt(v),3) for v in c]
                        for c in simulation.list_data[-1]["sim_votes"]["var"]]
        print_table(sdev_votes, h, const_names, out)

        print("\nVote shares")
        sdev_vote_shares = [["{:.1%}".format(sqrt(s)) for s in c[:-1]]
                            for c in simulation.list_data[-1]["sim_shares"]["var"]]
        print_table(sdev_vote_shares, h[:-1], const_names, out)

        print("\nConstituency seats")
        sdev_const_seats = [[round(sqrt(s),3) for s in c]
                            for c in simulation.list_data[r]["const_seats"]["var"]]
        print_table(sdev_const_seats, h, const_names, out)

        print("\nAdjustment seats")
        sdev_adj_seats = [[round(sqrt(s),3) for s in c]
                            for c in simulation.list_data[r]["adj_seats"]["var"]]
        print_table(sdev_adj_seats, h, const_names, out)

        print("\nTotal seats")
        sdev_total_seats = [[round(sqrt(s),3) for s in c]
                            for c in simulation.list_data[r]["total_seats"]["var"]]
        print_table(sdev_total_seats, h, const_names, out)

        print("\nSeat shares")
        var_seat_shares = simulation.list_data[r]["seat_shares"]["var"]
        shares = [["{:.1%}".format(s) for s in c[:-1]]
                    for c in var_seat_shares]
        print_table(shares, h[:-1], const_names, out)

        sdev_seat_shares = [["{:.1%}".format(sqrt(s)) for s in c[:-1]]
                            for c in var_seat_shares]
        print_table(sdev_seat_shares, h[:-1], const_names, out)

        #print("\nVotes added to change results")
        #print_table(simulation.votes_to_change, h[:-1], const_names[:-1], out)

def simulation_to_xlsx(simulation, filename):
    """Write detailed information about a simulation to an xlsx file."""
    workbook = xlsxwriter.Workbook(filename)

    r_format = workbook.add_format()
    r_format.set_rotation(90)
    r_format.set_align('center')
    r_format.set_align('vcenter')
    r_format.set_text_wrap()
    r_format.set_bold()
    r_format.set_font_size(12)

    h_format = workbook.add_format()
    h_format.set_align('center')
    h_format.set_bold()
    h_format.set_font_size(14)

    cell_format = workbook.add_format()
    cell_format.set_align('right')


    def write_matrix(worksheet, startrow, startcol, matrix, cformat):
        for c in range(len(matrix)):
            for p in range(len(matrix[c])):
                if matrix[c][p] != 0:
                    worksheet.write(startrow+c, startcol+p, matrix[c][p],
                                    cformat)

        return c, p

    def draw_block(worksheet, row, col, heading, xheaders, yheaders, matrix):
        worksheet.merge_range(row, col, row, col+len(xheaders), heading,
                                h_format)
        worksheet.write_row(row+1, col+1, xheaders, cell_format)
        worksheet.write_column(row+2, col, yheaders, cell_format)
        write_matrix(worksheet, row+2, col+1, matrix, cell_format)


    for r in range(len(simulation.e_rules)):
        method_name = simulation.e_rules[r]["adjustment_method"]
        worksheet = workbook.add_worksheet(method_name)
        const_names = simulation.e_rules[r]["constituency_names"] + ["Total"]
        parties = simulation.e_rules[r]["parties"] + ["Total"]

        # Reference data:
        xtd_votes = simulation.xtd_votes

        toprow = 3

        # Reference data
        worksheet.merge_range(toprow, 0, len(const_names)+toprow+1, 0,
                                "Reference data", r_format)

        col = 2
        draw_block(worksheet, toprow, col, "Votes", parties, const_names, xtd_votes)

        m_shares = [["{:.1%}".format(v/const_votes[-1])
                    for v in const_votes[:-1]] for const_votes in xtd_votes]
        col += len(parties)+2
        draw_block(worksheet, toprow, col, "Vote shares", parties, const_names, m_shares)

        col += len(parties)+2
        draw_block(worksheet, toprow, col, "Constituency seats", parties, const_names, simulation.base_allocations[r]["const_seats"])

        col += len(parties)+2
        draw_block(worksheet, toprow, col, "Adjustment seats", parties, const_names, simulation.base_allocations[r]["adj_seats"])

        col += len(parties)+2
        draw_block(worksheet, toprow, col, "Total seats", parties, const_names, simulation.base_allocations[r]["total_seats"])

        m_seat_shares = [["{:.1%}".format(s/seats[-1]) for s in seats[:-1]]
                         for seats in simulation.base_allocations[r]["total_seats"]]
        col += len(parties)+2
        draw_block(worksheet, toprow, col, "Seat shares", parties, const_names, m_seat_shares)


        # Now doing simulation results:
        toprow += len(const_names)+3

        worksheet.merge_range(toprow, 0, len(const_names)+toprow+1, 0,
                                "Averages from simulation", r_format)

        col = 2
        draw_block(worksheet, toprow, col, "Votes", parties, const_names, simulation.list_data[-1]["sim_votes"]["avg"])

        col += len(parties)+2
        draw_block(worksheet, toprow, col, "Vote shares", parties, const_names, simulation.list_data[-1]["sim_shares"]["avg"])

        col += len(parties)+2
        draw_block(worksheet, toprow, col, "Constituency seats", parties, const_names, simulation.list_data[r]["const_seats"]["avg"])

        col += len(parties)+2
        draw_block(worksheet, toprow, col, "Adjustment seats", parties, const_names, simulation.list_data[r]["adj_seats"]["avg"])

        col += len(parties)+2
        draw_block(worksheet, toprow, col, "Total seats", parties, const_names, simulation.list_data[r]["total_seats"]["avg"])

        m_seat_shares = [["{:.1%}".format(s) for s in const_shares[:-1]]
                         for const_shares in simulation.list_data[r]["seat_shares"]["avg"]]
        col += len(parties)+2
        draw_block(worksheet, toprow, col, "Seat shares", parties, const_names, m_seat_shares)



        # Standard deviations:
        sdev_votes = [[round(sqrt(v),3) for v in c]
                        for c in simulation.list_data[-1]["sim_votes"]["var"]]
        sdev_vote_shares = [["{:.1%}".format(sqrt(s)) for s in c[:-1]]
                                for c in simulation.list_data[-1]["sim_shares"]["var"]]
        sdev_const_seats = [[round(sqrt(v),3) for v in c]
                                for c in simulation.list_data[r]["const_seats"]["var"]]
        sdev_adj_seats = [[round(sqrt(v),3) for v in c]
                            for c in simulation.list_data[r]["adj_seats"]["var"]]
        sdev_total_seats = [[round(sqrt(v),3) for v in c]
                                for c in simulation.list_data[r]["total_seats"]["var"]]
        sdev_seat_shares = [["{:.1%}".format(sqrt(s)) for s in c[:-1]]
                                for c in simulation.list_data[r]["seat_shares"]["var"]]

        toprow += len(const_names)+4
        row = copy(toprow)
        col = 2
        worksheet.merge_range(row+1, 0, len(const_names)+row+1, 0,
                            "Standard deviations from simulation", r_format)
        worksheet.merge_range(row, col, row, col+len(parties),
                                "Votes", h_format)
        row += 1
        worksheet.write_row(row, col+1, parties, cell_format)
        row += 1
        worksheet.write_column(row, col, const_names, cell_format)
        for const_votes in sdev_votes:
            worksheet.write_row(row, col+1, const_votes, cell_format)
            row += 1
        row = copy(toprow)
        col += len(parties)+2
        worksheet.merge_range(row, col, row, col+len(parties)-1,
                                "Vote shares", h_format)
        row += 1
        worksheet.write_row(row, col+1, parties[:-1], cell_format)
        row += 1
        worksheet.write_column(row, col, const_names, cell_format)
        for const_vote_shares in sdev_vote_shares:
            worksheet.write_row(row, col+1, const_vote_shares, cell_format)
            row += 1
        row = copy(toprow)
        col += len(parties)+1
        worksheet.merge_range(row, col, row, col+len(parties),
                                "Constituency seats", h_format)
        row += 1
        worksheet.write_row(row, col+1, parties, cell_format)
        row += 1
        worksheet.write_column(row, col, const_names, cell_format)
        for seats in sdev_const_seats:
            worksheet.write_row(row, col+1, seats, cell_format)
            row += 1
        row = copy(toprow)
        col += len(parties)+2
        worksheet.merge_range(row, col, row, col+len(parties),
                                "Adjustment seats", h_format)
        row += 1
        worksheet.write_row(row, col+1, parties, cell_format)
        row += 1
        worksheet.write_column(row, col, const_names, cell_format)
        for seats in sdev_adj_seats:
            worksheet.write_row(row, col+1, seats, cell_format)
            row += 1
        row = copy(toprow)
        col += len(parties)+2
        worksheet.merge_range(row, col, row, col+len(parties),
                                "Total seats", h_format)
        row += 1
        worksheet.write_row(row, col+1, parties, cell_format)
        row += 1
        worksheet.write_column(row, col, const_names, cell_format)
        for seats in sdev_total_seats:
            worksheet.write_row(row, col+1, seats, cell_format)
            row += 1
        row = copy(toprow)
        col += len(parties)+2
        worksheet.merge_range(row, col, row, col+len(parties)-1,
                                "Seat shares", h_format)
        row += 1
        worksheet.write_row(row, col+1, parties[:-1], cell_format)
        row += 1
        worksheet.write_column(row, col, const_names, cell_format)
        for shares in sdev_seat_shares:
            worksheet.write_row(row, col+1, shares, cell_format)
            row += 1


    workbook.close()

ADJUSTMENT_METHODS = {
    "alternating-scaling": alternating_scaling,
    "relative-superiority": relative_superiority,
    "nearest-neighbor": nearest_neighbor,
    "monge": monge,
    "icelandic-law": icelandic_law,
    "norwegian-law": norwegian_law,
    "norwegian-icelandic": norwegian_icelandic,
    "opt-entropy": opt_entropy,
    "switching": switching,
    "var-alt-scal": var_alt_scal,
    "pure-vote-ratios": pure_vote_ratios,
}
