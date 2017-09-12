import React, { Component } from 'react';
import {
  Collapse,
  Navbar,
  NavbarToggler,
  NavbarBrand,
  Nav,
  NavItem,
  NavLink,
  Container,
  Row,
  Col,
  Jumbotron,
  Button
} from 'reactstrap';

import Client from '../client'

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
        <Navbar color="inverse" inverse toggleable>
          <NavbarToggler right onClick={this.toggle} />
          <NavbarBrand href="/">Votesim</NavbarBrand>
          <Collapse isOpen={this.state.isOpen} navbar>
            <Nav className="ml-auto" navbar>
              <NavItem>
                <NavLink href="https://github.com/smari/voting">Github</NavLink>
              </NavItem>
            </Nav>
          </Collapse>
        </Navbar>
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
