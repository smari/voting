
from random import betavariate

from table_util import add_totals, find_xtd_shares


def beta_distribution(
    base_votes, #2d - votes for each list,
    stbl_param  #stability parameter in range (1,->)
):
    """
    Generate a set of votes with beta distribution,
    using 'base_votes' as reference.
    """
    assert 1<stbl_param
    xtd_votes = add_totals(base_votes)
    xtd_shares = find_xtd_shares(xtd_votes)

    generated_votes = []
    for c in range(len(base_votes)):
        s = 0
        generated_votes.append([])
        for p in range(len(base_votes[c])):
            mean_beta_distr = xtd_shares[c][p]
            assert 0 <= mean_beta_distr and mean_beta_distr <= 1
            if 0 < mean_beta_distr and mean_beta_distr < 1:
                alpha, beta = beta_params(mean_beta_distr, stbl_param)
                share = betavariate(alpha, beta)
            else:
                share = mean_beta_distr #either 0 or 1
            generated_votes[c].append(int(share*xtd_votes[c][-1]))

    return generated_votes

def beta_params(mean, stability_parameter):
    assert 0<mean and mean<1
    assert 1<stability_parameter

    #make sure alpha and beta >1 to ensure nice probability distribution
    lower_mean = mean if mean<=0.5 else 1-mean
    assert 0<lower_mean and lower_mean<=0.5

    lifting_factor = 1 + 1.0/lower_mean
    assert lifting_factor >= 3
    assert lifting_factor >= 1+1/mean
    assert lifting_factor >= 1+1/(1-mean)

    weight = lifting_factor*stability_parameter - 1
    assert weight > 2
    assert weight > 1/mean
    assert weight > 1/(1-mean)

    alpha = mean*weight
    beta = (1-mean)*weight
    #note that weight=alpha+beta, aside from rounding errors
    assert alpha>1
    assert beta>1
    return alpha, beta
