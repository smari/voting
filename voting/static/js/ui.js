var RBS = ReactBootstrap;

var preset_elections = {
    "Icelandic Parliamentary Elections 2003": {
        "constituencies": [
            {
                "id": genRandomId(),
                "name": "Norðvestur",
                "primarySeats": 9,
                "adjustmentSeats": 1,
                "votes": [
                    {"id": 0, "votes": 4057},
                    {"id": 1, "votes": 5532},
                    {"id": 2, "votes": 2666},
                    {"id": 3, "votes": 122},
                    {"id": 4, "votes": 4346},
                    {"id": 5, "votes": 0},
                    {"id": 6, "votes": 1987},
                ]
            },
            {
                "id": genRandomId(),
                "name": "Norðaustur",
                "primarySeats": 9,
                "adjustmentSeats": 1,
                "votes": [
                    {"id": 0, "votes": 7722},
                    {"id": 1, "votes": 5544},
                    {"id": 2, "votes": 1329},
                    {"id": 3, "votes": 136},
                    {"id": 4, "votes": 5503},
                    {"id": 5, "votes": 0},
                    {"id": 6, "votes": 3329},
                ]
            },
            {
                "id": genRandomId(),
                "name": "Suður",
                "primarySeats": 9,
                "adjustmentSeats": 1,
                "votes": [
                    {"id": 0, "votes": 5934},
                    {"id": 1, "votes": 7307},
                    {"id": 2, "votes": 2188},
                    {"id": 3, "votes": 166},
                    {"id": 4, "votes": 7426},
                    {"id": 5, "votes": 844},
                    {"id": 6, "votes": 1167},
                ]
            },
            {
                "id": genRandomId(),
                "name": "Suðvestur",
                "primarySeats": 9,
                "adjustmentSeats": 2,
                "votes": [
                    {"id": 0, "votes": 6387},
                    {"id": 1, "votes": 16456},
                    {"id": 2, "votes": 2890},
                    {"id": 3, "votes": 399},
                    {"id": 4, "votes": 14029},
                    {"id": 5, "votes": 0},
                    {"id": 6, "votes": 2671},
                ]
            },
            {
                "id": genRandomId(),
                "name": "Reykjavík suður",
                "primarySeats": 9,
                "adjustmentSeats": 2,
                "votes": [
                    {"id": 0, "votes": 4185},
                    {"id": 1, "votes": 14029},
                    {"id": 2, "votes": 2448},
                    {"id": 3, "votes": 504},
                    {"id": 4, "votes": 12286},
                    {"id": 5, "votes": 0},
                    {"id": 6, "votes": 3438},
                ]
            },
            {
                "id": genRandomId(),
                "name": "Reykjavík norður",
                "primarySeats": 9,
                "adjustmentSeats": 2,
                "votes": [
                    {"id": 0, "votes": 4199},
                    {"id": 1, "votes": 12833},
                    {"id": 2, "votes": 2002},
                    {"id": 3, "votes": 464},
                    {"id": 4, "votes": 13110},
                    {"id": 5, "votes": 0},
                    {"id": 6, "votes": 3537},
                ]
            }
        ],
        "parties": [
            {"id": 0, "name": "B"},
            {"id": 1, "name": "D"},
            {"id": 2, "name": "F"},
            {"id": 3, "name": "N"},
            {"id": 4, "name": "S"},
            {"id": 5, "name": "T"},
            {"id": 6, "name": "U"},
        ],
        "settings": {
            "primaryTallyMethod": "dhondt",
            "adjustmentTallyMethod": "iceland",
        }
    }
}


var VotesConstituency = React.createClass({
    remove: function() {
        this.props.removeConstituency(this.props.data.id);
    },
    setName: function(e) {
        this.props.setConstituencyName(this.props.data.id, e.target.value);
    },
    setPartyVotes: function(e) {
        this.props.setPartyVotes(this.props.data.id, e.target.dataset.party, e.target.value)
    },
    getPartyVotes: function(party) {
        for (var vote in this.props.data.votes) {
            if (this.props.data.votes[vote].id == party) {
                return this.props.data.votes[vote].votes;
            }
        }
        return 0;
    },
    setPrimarySeats: function(e) {
        this.props.setPrimarySeats(this.props.data.id, e.target.value);
    },
    setAdjustmentSeats: function(e) {
        this.props.setAdjustmentSeats(this.props.data.id, e.target.value);
    },
    render: function() {
        var self = this;
        var partyFields = this.props.parties.map(function(party) {
            return (
                <td>
                    <input
                        className="vote-field"
                        data-party={party.id}
                        value={self.getPartyVotes(party.id)}
                        onChange={self.setPartyVotes}
                        />
                </td>
            )
        });

        return (
            <tr>
                <th>
                    <input
                        value={this.props.data.name}
                        onChange={this.setName}/>
                </th>
                <td>
                    <input
                        className="vote-field"
                        value={this.props.data.primarySeats}
                        onChange={this.setPrimarySeats}/>
                </td>
                <td>
                    <input
                        className="vote-field"
                        value={this.props.data.adjustmentSeats}
                        onChange={this.setAdjustmentSeats}/>
                </td>
                {partyFields}
                <td><a className="btn btn-sm btn-warning" onClick={this.remove}>Remove</a></td>
            </tr>
        );
    }
});

var VotesToolbar = React.createClass({
    render: function() {
        var presets = [];
        for (var p in preset_elections) {
            presets.push(<li><a href="#" data-preset={p} onClick={this.props.setPreset}>{p}</a></li>);
        }

        return (
            <div className="btn-toolbar" role="toolbar" aria-label="...">
                <a className="btn btn-default" onClick={this.props.addConstituency}>Add constituency</a>
                <a className="btn btn-default" onClick={this.props.addParty}>Add party</a>
                <a className="btn btn-warning" onClick={this.props.votesReset}>Reset</a>

                <div className="dropdown pull-right">
                    <a className="btn btn-default" id="dLabel" data-target="#" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">
                        Presets
                        <span className="caret"></span>
                    </a>

                    <ul className="dropdown-menu" aria-labelledby="dLabel">
                        {presets}
                    </ul>
                </div>

            </div>
        )
    }
});

var VotesTable = React.createClass({
    setPartyName: function(e) {
        this.props.setPartyName(e.target.dataset.id, e.target.value);
    },
    removeParty: function(e) {
        this.props.removeParty(e.target.dataset.id);
    },

    render: function() {
        var self = this;
        var constituencyNodes = this.props.data.constituencies.map(function(constituency) {
            return (
                <VotesConstituency
                    data={constituency}
                    parties={self.props.data.parties}
                    removeConstituency={self.props.removeConstituency}
                    setConstituencyName={self.props.setConstituencyName}
                    setAdjustmentSeats={self.props.setAdjustmentSeats}
                    setPrimarySeats={self.props.setPrimarySeats}
                    setPartyVotes={self.props.setPartyVotes}
                    />
            );
        });
        var partyNodes = this.props.data.parties.map(function(party) {
            return (
                <th>
                    <input
                        className="vote-field"
                        data-id={party.id}
                        value={party.name}
                        onChange={self.setPartyName}
                        />
                    <a
                        className="btn btn-xs btn-warning"
                        data-id={party.id}
                        onClick={self.removeParty}
                        >Remove</a>
                </th>
            );
        });

        return (
            <table className="table table-bordered table-hover table-striped">
                <thead>
                <tr>
                    <th>Constituency</th>
                    <th>Seats</th>
                    <th>Adjustment seats</th>
                    {partyNodes}
                </tr>
                </thead>
                <tbody>
                {constituencyNodes}
                </tbody>
            </table>
        );
    }
});

var VotesSettings = React.createClass({
    setPrimaryTallyMethod: function(e) {
        this.props.setPrimaryTallyMethod(e.target.value);
    },

    setAdjustmentTallyMethod: function(e) {
        this.props.setAdjustmentTallyMethod(e.target.value);
    },

    render: function() {
        var primaryTallyMethods = [];
        var adjustmentTallyMethods = [];

        for (var id in this.props.primaryTallyMethods) {
            var method = this.props.primaryTallyMethods[id];
            primaryTallyMethods.push(<option value={id}>{method.name}</option>);
        }

        for (var id in this.props.adjustmentTallyMethods) {
            var method = this.props.adjustmentTallyMethods[id]
            adjustmentTallyMethods.push(<option value={id}>{method.name}</option>);
        }

        return (
            <form>
                <div className="form-group">
                    <label htmlFor="primaryTallyMethod">Primary Tally Method</label>
                    <select
                        className="form-control"
                        id="primaryTallyMethod"
                        onChange={this.setPrimaryTallyMethod}
                        >
                        {primaryTallyMethods}
                    </select>
                </div>
                <div className="form-group">
                    <label htmlFor="adjustmentTallyMethod">Adjustment Seats Tally Method</label>
                    <select
                        className="form-control"
                        id="adjustmentTallyMethod"
                        onChange={this.setAdjustmentTallyMethod}
                        >
                        {adjustmentTallyMethods}
                    </select>
                </div>
            </form>
        )
    }
});

var VotesResults = React.createClass({
    getPartyById: function(id) {
        for (var p in this.props.data.parties) {
            if (this.props.data.parties[p].id == id) {
                return this.props.data.parties[p];
            }
        }
        return {"id": -1, "name": "Error", "votes": 0};
    },

    render: function() {
        var res = "";
        var tallyMethod = this.props.primaryTallyMethods[this.props.data.settings.primaryTallyMethod];
        var constituencies = [];
        for (var c in this.props.data.constituencies) {
            var cons = this.props.data.constituencies[c];
            var consvotes = [];
            var rounds = tallyMethod.func(cons.votes, cons.primarySeats);

            var rv = [];
            rv.push(<th>Seat allocations</th>);
            for (var cand in this.props.data.parties) {
                var c = this.props.data.parties[cand];
                rv.push(<th>{c.name}</th>);
            }
            rv.push(<th>Winner</th>);
            consvotes.push(<thead><tr>{rv}</tr></thead>);
            var rb = [];
            for (var round in rounds) {
                var rv = [];
                var roundno = parseInt(round)+1;
                rv.push(<th>Seat {roundno}</th>);
                for (var cand in rounds[round].votes) {
                    var v = Math.round(rounds[round].votes[cand], 2)
                    rv.push(<td>{v}</td>);
                }
                rv.push(<td>{this.getPartyById(rounds[round].winner).name}</td>);
                rb.push(
                    <tr>
                        {rv}
                    </tr>
                )
            }
            consvotes.push(<tbody>{rb}</tbody>)

            var conswinners = [];
            var winners = {};
            for (var party in this.props.data.parties) {
                winners[this.props.data.parties[party].id] = 0;
            }
            for (var round in rounds) {
                winners[rounds[round].winner]++;
            }
            for (var winner in winners) {
                conswinners.push(<li>{this.getPartyById(winner).name}: {winners[winner]}</li>);
            }


            constituencies.push(
                <div>
                    <h2>{cons.name}</h2>
                    <table className="table table-bordered table-striped">
                        {consvotes}
                    </table>
                    <ul>
                        {conswinners}
                    </ul>
                </div>
            )
        }

        return (
            <div>
                {constituencies}
                <pre>{res}</pre>
            </div>
        )
    }
});

var VotingSimulator = React.createClass({
    getInitialState: function() {
        return {
            key: 1,
            constituencies: [],
            parties: [],
            settings: {
                "primaryTallyMethod": "dhondt",
                "adjustmentTallyMethod": "iceland",
            }
        };
    },

    primaryTallyMethods: {
        "dhondt": {"name": "D'Hondt", "func": dhondt},
        "sainte-lague": {"name": "Sainte-Laguë", "func": sainte_lague},
        "swedish": {"name": "Swedish Sainte-Laguë", "func": swedish_sainte_lague},
    },
    adjustmentTallyMethods: {
        "iceland": {"name": "Icelandic method", "func": null},
    },

    handleSelect(key) {
        this.setState({key});
    },

    render: function() {
        return (
        <RBS.Tabs activeKey={this.state.key} onSelect={this.handleSelect} id="tabs">
          <RBS.Tab eventKey={1} title="Votes">
            <VotesToolbar
                addConstituency={this.addConstituency}
                addParty={this.addParty}
                votesReset={this.votesReset}
                setPreset={this.setPreset}
            />
            <VotesTable
                data={this.state}
                removeConstituency={this.removeConstituency}
                removeParty={this.removeParty}
                setConstituencyName={this.setConstituencyName}
                setAdjustmentSeats={this.setAdjustmentSeats}
                setPrimarySeats={this.setPrimarySeats}
                setPartyName={this.setPartyName}
                setPartyVotes={this.setPartyVotes}
            />
          </RBS.Tab>

          <RBS.Tab eventKey={2} title="Settings">
            <VotesSettings
                setPrimaryTallyMethod={this.setPrimaryTallyMethod}
                setAdjustmentTallyMethod={this.setAdjustmentTallyMethod}
                primaryTallyMethods={this.primaryTallyMethods}
                adjustmentTallyMethods={this.adjustmentTallyMethods}
                data={this.state}
            />
          </RBS.Tab>

          <RBS.Tab eventKey={3} title="Results">
            <VotesResults
              primaryTallyMethods={this.primaryTallyMethods}
              adjustmentTallyMethods={this.adjustmentTallyMethods}
              data={this.state}
            />
          </RBS.Tab>
        </RBS.Tabs>
        )
    },

    removeConstituency: function(id) {
        var con = this.state.constituencies.filter(function( obj ) {
            return obj.id !== id;
        });
        this.setState({constituencies: con});
    },

    removeParty: function(id) {
        var con = this.state.parties.filter(function( obj ) {
            return obj.id !== id;
        });
        this.setState({parties: con});
    },

    setPrimaryTallyMethod: function(method) {
        var set = jQuery.extend(true, {}, this.state.settings);
        set.primaryTallyMethod = method;
        this.setState({settings: set});
    },

    setAdjustmentTallyMethod: function(method) {
        var set = jQuery.extend(true, {}, this.state.settings);
        set.adjustmentTallyMethod = method;
        this.setState({settings: set});
    },

    setConstituencyName: function(id, name) {
        var con = this.state.constituencies.map(function( obj ) {
            if (obj.id == id) {
                obj.name = name;
            }
            return obj;
        });
        this.setState({constituencies: con});
    },

    setPrimarySeats: function(id, primarySeats) {
        var con = this.state.constituencies.map(function( obj ) {
            if (obj.id == id) {
                obj.primarySeats = primarySeats;
            }
            return obj;
        });
        this.setState({constituencies: con});
    },

    setAdjustmentSeats: function(id, adjustmentSeats) {
        var con = this.state.constituencies.map(function( obj ) {
            if (obj.id == id) {
                obj.adjustmentSeats = adjustmentSeats;
            }
            return obj;
        });
        this.setState({constituencies: con});
    },

    setPartyName: function(id, name) {
        var con = this.state.parties.map(function( obj ) {
            if (obj.id == id) {
                obj.name = name;
            }
            return obj;
        });
        this.setState({parties: con});
    },

    addConstituency: function() {
        var constituencies = this.state.constituencies.slice();
        var votes = [];
        for (var p in this.state.parties) {
            votes.push({"id": this.state.parties[p].id, "votes": 0});
        }
        constituencies.push({"id": genRandomId(), "name": "New constituency", "votes": votes});
        this.setState({constituencies: constituencies});
    },

    addParty: function() {
        var parties = this.state.parties.slice();
        var partyId = genRandomId();
        var party = {"id": partyId, "name": "?"};
        parties.push(party);
        this.setState({parties: parties});
        var con = this.state.constituencies.map(function(cons) {
            cons.votes.push({"id": partyId, "votes": 0});
            return cons;
        });

        this.setState({constituencies: con});
    },

    setPartyVotes: function(constituency, party, votes) {
        var self = this;
        var con = this.state.constituencies.map(function( obj ) {
            if (obj.id == constituency) {
                var found = false;
                for(var i = 0; i < obj.votes.length; i++) {
                    if (obj.votes[i].id == party) {
                        found = true;
                        break;
                    }
                }

                if (found) {
                    obj.votes = obj.votes.map(function(v) {
                        if (v.id == party) {
                            v.votes = votes;
                        }
                        return v;
                    });
                } else {
                    obj.votes.push({"id": party, "votes": votes});
                }
            }
            return obj;
        });
        this.setState({constituencies: con});
    },

    votesReset: function() {
        this.setState({constituencies: []});
        this.setState({parties: []});
    },

    setPreset: function(e) {
        var preset = e.target.dataset.preset;
        if (!preset_elections[preset]) {
            alert('Preset ' + preset + ' does not exist');
        }
        var pr = preset_elections[preset];
        this.setState({constituencies: pr.constituencies});
        this.setState({parties: pr.parties});
        this.setState({settings: pr.settings});
    },

});

ReactDOM.render(
    <VotingSimulator />,
    document.getElementById('votes')
);

function genRandomId() {
    var length = 8;
    var chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz'.split('');

    if (! length) {
        length = Math.floor(Math.random() * chars.length);
    }

    var str = '';
    for (var i = 0; i < length; i++) {
        str += chars[Math.floor(Math.random() * chars.length)];
    }
    return str;
}
