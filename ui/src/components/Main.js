import React, { Component } from 'react';
import {
  Container,
  Row,
  Col,
  Jumbotron,
  Button
} from 'reactstrap';

import Client from '../client'
import Navigation from './Navigation'
import Settings from './Settings'
import Home from './Home'

import {
  BrowserRouter as Router,
  Route,
  Link,
  Switch
} from 'react-router-dom'

import uuid from 'uuid'

class Main extends Component {
  constructor(props) {
    super(props)
    this.setPrimaryDividerRule = this.setPrimaryDividerRule.bind(this)
    this.setAdjustmentDividerRule = this.setAdjustmentDividerRule.bind(this)
    this.setAdjustmentMethod = this.setAdjustmentMethod.bind(this)
    this.setAdjustmentThreshold = this.setAdjustmentThreshold.bind(this)
    this.state = {
      constituencies: [],
      parties: [],
      electionRules: {},
      simulationRules: {},
      presets: [],
      adjustmentMethods: {},
      dividerRules: {},
      votes: []
    }
  }


  componentDidMount() {
      Client.getCapabilities( (data) => {
        console.log("Found presets: ", data.presets);
        this.setState({
            adjustmentMethods: data.capabilities.adjustment_methods,            
            dividerRules: data.capabilities.divider_rules,
            electionRules: data.election_rules,
            simulationRules: data.simulation_rules,
            presets: data.presets,
            errors: data.presets.filter(p => {if('error' in p) return p.error})
        })
      });
  }
  setPrimaryDividerRule(val) {
    console.log(val)
  }

  setAdjustmentDividerRule(val) {
    console.log(val)
  }

  setAdjustmentMethod(val) {
    console.log(val)
    //this.setState({electionRules[]})
  }
  setAdjustmentThreshold(e) {
    const rules = this.state.electionRules
    rules.adjustment_threshold = e.target.value
    console.log(rules.adjustment_threshold)
    this.setState({electionRules: rules})

  }
  render() {
    return (
      <div>
        <Navigation props={this.state} />
        <Jumbotron>
          <Container>          
            <Route exact path='/' component={Home} />              
            <Route path='/settings' render={(props) => (
              <Settings
                setAdjustmentMethod={this.setAdjustmentMethod}
                setAdjustmentDividerRule={this.setAdjustmentDividerRule}
                setPrimaryDividerRule={this.setDividerRule}
                electionRules={this.state.electionRules}
                adjustmentMethods={this.state.adjustmentMethods}
                dividerRules={this.state.dividerRules}
                setAdjustmentThreshold={this.setAdjustmentThreshold}
                {...props} />
            )} />

          </Container>
        </Jumbotron>
      </div>
    );
  }
}

export default Main;
