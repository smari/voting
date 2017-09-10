// THIS SHOULD BE DELETED IT IS OBSOLETE.

candidates = [];
constituencies = [];

function prop_assign(candidates, seats, divstart, divincrement) {
    var rounds = [];
    var orig_votes = candidates.map(function(x) { return parseInt(x.votes); });
    var alloc_votes = candidates.map(function(x) { return parseInt(x.votes); });
    var divisor = candidates.map(function(x) { return divstart; });
    var candidx = candidates.map(function(x) { return x.id; });

    for (var i = 1; i <= seats; i++) {
        var maxval = Math.max.apply(null, alloc_votes);
        var idx = alloc_votes.indexOf(maxval);
        var vs = alloc_votes.map(function(x) { return x; });
        res = {
            "maxval": maxval,
            "votes": vs,
            "winner": candidx[idx],
            "divisor": divisor[idx]
        };
        rounds.push(res);
        // console.log(res);
        divisor[idx] += divincrement;
        alloc_votes[idx] = orig_votes[idx] / divisor[idx];
    }

    return rounds;
}


function dhondt(candidates, seats) {
    return prop_assign(candidates, seats, 1, 1);
}

function sainte_lague(candidates, seats) {
    return prop_assign(candidates, seats, 1, 2);
}

function swedish_sainte_lague(candidates, seats) {
    return prop_assign(candidates, seats, 1.4, 2);
}

function pad(str, len, padder) {
    padder = padder || " ";
    // if (str.length > len) {
    //    str.substr(0,len);
    //}
    while (str.length <= len) { str = padder + str; }
    return str;
}

function pretty_print_rounds(rounds, candidates) {
    var s = "            | ";
    var r = "      Votes | ";
    var sep = "            |";
    var out = "";
    for (var candidate in candidates) {
        s += pad(candidates[candidate].name, 7) + " | ";
        r += pad(candidates[candidate].votes.toString(), 7) + " | ";
        sep += pad("-", 8, "-") + "-|";
    }
    out += sep + "\n" + s + "\n" + sep + "\n" + r + "\n" + sep + "\n";
    for (var round in rounds) {
        roundno = parseInt(round)+1;
        r = " " + pad("Round " + roundno, 9) + " | ";
        for (candidate in candidates) {
            r += pad(Math.round(rounds[round].votes[candidate], 2).toString(), 7) + " | ";
        }
        out += r + "   " + candidates[rounds[round].winner].name + "\n";
        out += sep + "\n";
    }

    return out;
}

function pretty_print_results(rounds, candidates) {
    var out = "";
    var winners = {};
    for (candidate in candidates) {
        winners[candidates[candidate].name] = 0;
    }
    for (round in rounds) {
        winners[candidates[rounds[round].winner].name]++;
    }
    for (winner in winners) {
        out += pad(winner, 10) + ": " + winners[winner];
    }
    return out + "\n";
}
