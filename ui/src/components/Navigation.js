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

import { NavLink as RRNavLink } from 'react-router-dom';

import {Link} from 'react-router-dom';
import Settings from './Settings';


const Navigation = (props) => (
  <Navbar color="inverse" inverse toggleable>
    <NavbarToggler right onClick={this.toggle} />
    <NavbarBrand href="/">Votesim</NavbarBrand>
    <Collapse isOpen={props.isOpen} navbar>
      <Nav className="ml-auto" navbar>
        <NavItem>        
            <NavLink tag={Link} to="/settings">Settings</NavLink> 
        </NavItem>      
        <NavItem>
          <NavLink href="https://github.com/smari/voting">Github</NavLink>
        </NavItem>
      </Nav>
    </Collapse>
  </Navbar>
)

export default Navigation;