var RBS = ReactBootstrap;

/*
 * For design outline, see README.
 *
 */

var preset_elections = {};


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
    setdivider_rule: function(e) {
        this.props.setdivider_rule(e.target.value);
    },

    setadjustmentdivider_rule: function(e) {
        this.props.setadjustmentdivider_rule(e.target.value);
    },

    setadjustment_method: function(e) {
        this.props.setadjustment_method(e.target.value);
    },

    render: function() {
        var divider_rules = [];
        var adjustmentdivider_rules = [];
        var adjustment_methods = [];

        if (!this.props.data.capabilities_loaded) {
            return <div>Capabilities not loaded</div>;
        }

        for (var id in this.props.data.capabilities.divider_rules) {
            var method = this.props.data.capabilities.divider_rules[id];
            var checked = (id == this.props.data.rules.primary_divider);
            if (checked) {
              divider_rules.push(<option selected value={id}>{method}</option>);
            } else {
              divider_rules.push(<option value={id}>{method}</option>);
            }
        }

        for (var id in this.props.data.capabilities.divider_rules) {
            var method = this.props.data.capabilities.divider_rules[id];
            var checked = (id == this.props.data.rules.adjustment_divider);
            if (checked) {
              adjustmentdivider_rules.push(<option selected value={id}>{method}</option>);
            } else {
              adjustmentdivider_rules.push(<option value={id}>{method}</option>);
            }
        }

        for (var id in this.props.data.capabilities.adjustment_methods) {
            var method = this.props.data.capabilities.adjustment_methods[id]
            adjustment_methods.push(<option value={id}>{method}</option>);
            var checked = (id == this.props.data.rules.adjustment_method);
            if (checked) {
              adjustment_methods.push(<option selected value={id}>{method}</option>);
            } else {
              adjustment_methods.push(<option value={id}>{method}</option>);
            }
        }

        return (
            <RBS.Grid fluid={true}>
            <RBS.Row>
            <RBS.Col xs={8} md={6}>
                <form>
                    <div className="form-group">
                        <label htmlFor="divider_rule">Primary divider rule</label>
                        <select
                            className="form-control"
                            id="divider_rule"
                            onChange={this.setdivider_rule}
                            >
                            {divider_rules}
                        </select>
                    </div>
                    <div className="form-group">
                        <label htmlFor="adjustmentdivider_rule">Adjustment divider rule</label>
                        <select
                            className="form-control"
                            id="adjustmentdivider_rule"
                            onChange={this.setadjustmentdivider_rule}
                            >
                            {adjustmentdivider_rules}
                        </select>
                    </div>
                    <div className="form-group">
                        <label htmlFor="adjustment_method">Adjustment method</label>
                        <select
                            className="form-control"
                            id="adjustment_method"
                            onChange={this.setadjustment_method}
                            >
                            {adjustment_methods}
                        </select>
                    </div>
                </form>
            </RBS.Col>
            </RBS.Row>
            </RBS.Grid>
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
        var rules = this.props.data.rules;
        var caps = this.props.data.capabilities;

        if (!this.props.data.capabilities_loaded) {
            return <div>Capabilities not loaded</div>;
        }

        var tallyMethod = caps.divider_rules[rules.divider_rule];
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
        var init = {
            key: 1,
            constituencies: [],
            parties: [],
            rules: {},
            capabilities: {},
            capabilities_loaded: false
        };
        $.getJSON('/api/capabilities/', {}, this.getCapabilities);
        return init;
    },

    getCapabilities(data) {
      this.setState({
        capabilities: data.capabilities,
        rules: data.default_rules,
        capabilities_loaded: true
      })
      console.log("State: ", this.state);
    },

    handleSelect(key) {
        this.setState({key});
    },

    debugInfo() {
        console.log(this.state);
    },

    render: function() {
        return (
        <RBS.Tabs activeKey={this.state.key} onSelect={this.handleSelect} id="tabs">
          <RBS.Tab eventKey={2} title="Simulation">
            Not implemented.
          </RBS.Tab>

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

          <RBS.Tab eventKey={3} title="Election results">
            <VotesResults
              divider_rules={this.state.capabilities.divider_rules}
              adjustment_methods={this.adjustment_methods}
              data={this.state}
            />
          </RBS.Tab>

          <RBS.Tab eventKey={4} title="Visualization">
            Not implemented.
          </RBS.Tab>

          <RBS.Tab eventKey={5} title="Settings">
            <VotesSettings
                capabilities_loaded={this.state.capabilities_loaded}
                setdivider_rule={this.setdivider_rule}
                setadjustmentdivider_rule={this.setadjustmentdivider_rule}
                setadjustment_method={this.setadjustment_method}
                divider_rules={this.state.capabilities.divider_rules}
                adjustment_methods={this.adjustment_methods}
                data={this.state}
            />
          </RBS.Tab>
          <RBS.Button onClick={this.debugInfo}>
            Dump debug info
          </RBS.Button>
          <RBS.Button onClick={this.calculate}>
            Calculate
          </RBS.Button>
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

    setdivider_rule: function(method) {
        var set = jQuery.extend(true, {}, this.state.rules);
        set.primary_divider = method;
        this.setState({rules: set});
    },

    setadjustmentdivider_rule: function(method) {
        var set = jQuery.extend(true, {}, this.state.rules);
        set.adjustment_divider = method;
        this.setState({rules: set});
    },

    setadjustment_method: function(method) {
        var set = jQuery.extend(true, {}, this.state.rules);
        set.adjustment_method = method;
        this.setState({rules: set});
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
        this.setState({rules: pr.rules});
    },

    calculate: function() {
      var rules = this.state.rules
      $(function() {
        $.ajax({
          url: '/api/',
          type: "POST",
          data: JSON.stringify(rules),
          contentType: 'application/json; charset=utf-8',
          success: function(data) {
              console.log(data);
          },
          dataType: "json"
        });
      });
    }

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
