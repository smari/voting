import React, { Component } from 'react';

import {
  Collapse,
  Navbar,
  NavbarToggler,
  NavbarBrand,
  Nav,
  NavItem,
  NavLink
} from 'reactstrap';

const Navigation = (props) => (
  <Navbar color="inverse" inverse toggleable>
    <NavbarToggler right onClick={this.toggle} />
    <NavbarBrand href="/">Votesim</NavbarBrand>
    <Collapse isOpen={props.isOpen} navbar>
      <Nav className="ml-auto" navbar>
        <NavItem>
          <NavLink href="https://github.com/smari/voting">Github</NavLink>
        </NavItem>
      </Nav>
    </Collapse>
  </Navbar>
)

export default Navigation;