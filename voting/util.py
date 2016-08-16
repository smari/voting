#coding:utf-8
import random
import csv
import sys

def random_id(length = 8):
    chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz'
    s = "".join(random.sample(chars, length))
    return s


def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]

def load_constituencies(confile):
    csv_reader = unicode_csv_reader(confile)
    cons = []
    for row in csv_reader:
        try:
            assert(sum([int(x) for x in row[1:3]]) > 0)
        except:
            print row[1:3]
            raise Exception("Error loading constituency file: constituency seats and adjustment seats must add to a nonzero number.")
        cons.append({
            "name": row[0],
            "num_constituency_seats": int(row[1]),
            "num_adjustment_seats": int(row[2]),
            "num_total_seats": int(row[1])+int(row[2])})
    return cons

def load_votes(votefile, consts):
    csv_reader = unicode_csv_reader(votefile)
    parties = next(csv_reader)[1:]
    votes = []
    sys.stderr.write("Warning: When loading votes, no attempt is currently made to guarantee that the vote file lists constituencies in the same order as they are declared in the constituency file.\n")

    for row in csv_reader:
        try:
            assert(row[0] in [x["name"] for x in consts])
        except:
            raise Exception("Constituency '%s' not found in constituency file." % row[0])
        v = []
        for x in row[1:]:
            try:
                r = float(x)
            except:
                r = 0
            v.append(r)
        votes.append(v)

    return parties, votes
