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
    return (
      <div>
        <Navigation props={this.state} />
        <Jumbotron>
          <Container>
            <Row>
              <Col>
                <h1>Welcome to Votesim</h1>
                <p>
                  <Button
                    tag="a"
                    color="success"
                    size="large"
                    href="https://github.com/smari/voting"
                    target="_blank"
                  >
                    Let´s get it on
                  </Button>
                </p>
              </Col>
            </Row>
          </Container>
        </Jumbotron>
      </div>
    );
  }
}

export default Main;
