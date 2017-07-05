#coding:utf-8
import random
from backports import csv
import sys
import tabulate
import io


def random_id(length=8):
    chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz'
    s = "".join(random.sample(chars, length))
    return s


def read_csv(filename):
    with io.open(filename, mode="r", newline='', encoding='utf-8') as f:
        for row in csv.reader(f):
            yield [cell for cell in row]

def load_constituencies(confile):
    csv_reader = read_csv(confile)
    cons = []
    for row in csv_reader:
        try:
            assert(sum([int(x) for x in row[1:3]]) > 0)
        except:
            print(row[1:3])
            raise Exception("Error loading constituency file: "
                            "constituency seats and adjustment seats "
                            "must add to a nonzero number.")
        cons.append({
            "name": row[0],
            "num_constituency_seats": int(row[1]),
            "num_adjustment_seats": int(row[2]),
            "num_total_seats": int(row[1])+int(row[2])})
    return cons

def load_votes(votefile, consts):
    csv_reader = read_csv(votefile)
    parties = next(csv_reader)[1:]
    votes = []

    for row in csv_reader:
        try:
            assert(row[0] in [x["name"] for x in consts])
        except:
            print(row)
            raise Exception("Constituency '%s' not found in constituency file."
                            % row[0])
        v = []
        for x in row[1:]:
            try:
                r = float(x)
            except:
                r = 0
            v.append(r)
        votes.append(v)

    return parties, votes

def pretty_print_election(rules, election):
    header = ["Constituency"]
    header.extend(rules["parties"])
    if "constituencies" in rules:
        data = [[rules["constituencies"][c]["name"]]+election.results[c]
                for c in range(len(rules["constituencies"]))]
    else:
        data = [[rules["constituency_names"][c]]+election.results[c]
                for c in range(len(rules["constituency_names"]))]
    print(tabulate.tabulate(data, header, rules["output"]))
