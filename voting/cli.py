#coding:utf-8
"""
Command line interface for Voting.
"""
import click
import tabulate

import voting
import util

### Monkey patching CSV output mode into tabulate:
tabulate.tabulate_formats.append("csv")
tabulate._table_formats["csv"] = tabulate.TableFormat(
    lineabove=None, linebelowheader=None, linebetweenrows=None,
    linebelow=None, headerrow=tabulate.DataRow(begin=u'', sep=u',', end=u''),
    datarow=tabulate.DataRow(begin=u'', sep=u',', end=u''),
    padding=0, with_header_hide=None)


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    """Basic CLI."""
    if debug:
        click.echo('Debug mode is on')


@cli.command()
@click.option('--divider', required=True,
              type=click.Choice(voting.DIVIDER_RULES.keys()),
              help='Divider rule to use.')
@click.option('--adjustment-divider', default=None,
              type=click.Choice(voting.DIVIDER_RULES.keys()),
              help='Divider rule for adjustment seats. Defaults to primary.')
@click.option('--constituencies', required=True, type=click.File('r'),
              help='File with constituency data')
@click.option('--votes', required=True, type=click.File('r'),
              help='File with vote data to use as seed')
@click.option('--voters', required=True, type=click.File('r'),
              help='File with votes information')
@click.option('--simulations', default=100, help='How many simulations to run')
@click.option('--threshold', default=5,
              help='Threshold (in %%) for adjustment seats')
@click.option('--betavariancesquared', default=0.005)
@click.option('--partyweight', default=0.8)
@click.option('--output', default='simple',
              type=click.Choice(tabulate.tabulate_formats))
@click.option('--adjustment-method', '-m', multiple=True,
              type=click.Choice(voting.ADJUSTMENT_METHODS.keys()),
              required=True)
def simulate(votes, **kwargs):
    """Simulate elections"""

    pass
    # divider, adjustment_divider, constituencies, votes, voters,
    # simulations, threshold, betavariancesquared, partyweight, output,
    # adjustment_method

    # 1. Setup:
    #  - Load data files
    #  - Select methods
    # threshold *= 0.01
    # const = util.load_constituencies(constituencies)
    # parties, votes = util.load_votes(votes, const)
    #
    # divmethod = voting.DIVIDER_RULES[divider]
    # if not adjustment_divider:
    #     adjustment_divmethod = divmethod
    # else:
    #     adjustment_divmethod = voting.DIVIDER_RULES[adjustment_divider]
    #
    # for sim in range(simulations):
    #     print "\rSimulation %d" % sim,
    #     sys.stdout.flush()
    #
    #     for meth in adjustment_method:
    #         method = voting.ADJUSTMENT_METHODS[meth]
    #
    #         results = method(votes, v_const_seats, v_party_adjustment_seats,
    #                          m_allocations, adjustment_divmethod, threshold)

    # Output:
    #  - delta of entropy from optimal
    #  - delta of seats from optimal
    #  - smallest number of votes behind a seat
    #  - largest number of votes behind a seat
    #


@cli.command()
@click.option('--divider', required=True,
              type=click.Choice(voting.DIVIDER_RULES.keys()),
              help='Divider rule to use.')
@click.option('--adjustment-divider', default=None,
              type=click.Choice(voting.DIVIDER_RULES.keys()),
              help='Divider rule for adjustment seats. Defaults to primary.')
@click.option('--constituencies', required=True, type=click.File('r'),
              help='File with constituency data')
@click.option('--votes', required=True, type=click.File('r'),
              help='File with vote data')
@click.option('--threshold', default=5,
              help='Threshold (in %%) for adjustment seats')
@click.option('--output', default='simple',
              type=click.Choice(tabulate.tabulate_formats))
@click.option('--show-entropy', default=False, is_flag=True)
@click.option('--adjustment-method', '-m',
              type=click.Choice(voting.ADJUSTMENT_METHODS.keys()),
              required=True)
@click.option('--show-constituency-seats', is_flag=True)
def apportion(votes, **kwargs):
    """Do regular apportionment based on votes and constituency data."""
    rules = voting.Rules()
    kwargs["adjustment_divider"] = kwargs["adjustment_divider"] or kwargs["divider"]
    for arg, val in kwargs.iteritems():
        rules[arg] = val

    parties, votes = util.load_votes(votes, rules["constituencies"])
    rules["parties"] = parties
    election = voting.Election(rules, votes)
    election.run()

    header = ["Constituency"]
    header.extend(parties)
    print "\n=== %s ===" % (
        voting.adjustment_method_names[rules["adjustment_method"]])
    data = [[rules["constituencies"][c]["name"]]+election.results[c]
            for c in range(len(rules["constituencies"]))]
    print tabulate.tabulate(data, header, rules["output"])


if __name__ == '__main__':
    cli()
