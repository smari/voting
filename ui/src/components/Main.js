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
    super(props);

    this.toggle = this.toggle.bind(this);
    this.state = {
      isOpen: false
    };
  }
  
  toggle() {
    this.setState({
      isOpen: !this.state.isOpen
    });
  }

  componentDidMount() {
      Client.getCapabilities( (data) => {
          console.log("Found presets: ", data.presets);
          this.setState({
              capabilities: data.capabilities,
              election_rules: data.election_rules,
              simulation_rules: data.simulation_rules,
              presets: data.presets,
              capabilities_loaded: true,
              //errors: data.presets.map((p) => ('error' in p ? p.error: []))
              errors: data.presets.filter(p => {if('error' in p) return p.error})
          })
      });
  }
  render() {
    console.log(this.state)
    return (
      <div>
        <Navigation props={this.state} />
        <Jumbotron>
          <Container>          
            <Route exact path='/' component={Home} />              
            <Route path='/settings' render={(props) => (
              <Settings
                capabilitiesLoaded={this.state.capabilities_loaded}
                setDividerRule={this.setdivider_rule}
                setAdjustmentDividerRule={this.setadjustmentdivider_rule}
                setAdjustmentMethod={this.setadjustment_method}
                capabilities={this.state.capabilities}
                adjustmentMethods={this.adjustment_methods}
                data={this.state}
                {...props} />
            )} />

          </Container>
        </Jumbotron>
      </div>
    );
  }
}

export default Main;
