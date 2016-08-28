import click
import tabulate

import voting
import util

from copy import copy

### Monkey patching CSV output mode into tabulate:
tabulate.tabulate_formats.append("csv")
tabulate._table_formats["csv"] = tabulate.TableFormat(lineabove=None, linebelowheader=None, linebetweenrows=None, linebelow=None, headerrow=tabulate.DataRow(begin=u'', sep=u',', end=u''), datarow=tabulate.DataRow(begin=u'', sep=u',', end=u''), padding=0, with_header_hide=None)


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    if debug:
        click.echo('Debug mode is on')

@cli.command()
@click.option('--divider', required=True, type=click.Choice(voting.divider_rules.keys()), help='Divider rule to use.')
@click.option('--adjustment-divider', default=None, type=click.Choice(voting.divider_rules.keys()), help='Divider rule to use for adjustment seats. Leave blank to use same as primary method.')
@click.option('--constituencies', required=True, type=click.File('r'), help='File with constituency data')
@click.option('--votes', required=True, type=click.File('r'), help='File with vote data')
@click.option('--threshold', default=5, help='Threshold (in %%) for adjustment seats')
@click.option('--output', default='simple', type=click.Choice(tabulate.tabulate_formats))
@click.option('--show-entropy', default=False, is_flag=True)
@click.option('--adjustment-method', '-m', multiple=True, type=click.Choice(voting.adjustment_methods.keys()), required=True)
def apportion(divider, adjustment_divider, constituencies, votes, threshold, output, show_entropy, adjustment_method):
    """Do regular apportionment based on votes and constituency data."""

    # 1. Setup:
    #  - Load data files
    #  - Select methods
    threshold *= 0.01
    const = util.load_constituencies(constituencies)
    parties, votes = util.load_votes(votes, const)

    divmethod = voting.divider_rules[divider]
    if not adjustment_divider:
        adjustment_divmethod = divmethod
    else:
        adjustment_divmethod = voting.divider_rules[adjustment_divider]

    # 2. Primary method
    m_allocations, v_seatcount = voting.primary_seat_allocation(votes, const, parties, divmethod)

    # 3. Eliminate parties under thresholds from national votes
    v_elim_votes = voting.threshold_elimination_totals(votes, threshold)

    # 4. Find total number of seats in each constituency
    v_const_seats = [s["num_total_seats"] for s in const]

    # 4. Calculate adjustment seats
    v_party_adjustment_seats = voting.adjustment_seat_allocation(v_elim_votes, sum(v_const_seats), v_seatcount, adjustment_divmethod)

    # 5. Conduct adjustment method:
    for m in adjustment_method:
        method = voting.adjustment_methods[m]
        results = method(votes, v_const_seats, v_party_adjustment_seats, m_allocations, adjustment_divmethod, threshold)

        header = ["Constituency"]
        header.extend(parties)
        print "\n=== %s ===" % (voting.adjustment_method_names[m])
        data = [[const[c]["name"]]+results[c] for c in range(len(const))]
        print tabulate.tabulate(data, header, output)

        if show_entropy:
            e = voting.entropy(votes, results, divmethod)
            print "\nEntropy: ", e


if __name__ == '__main__':
    cli()
