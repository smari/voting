import React, { Component } from 'react';
import {
  Row,
  Col
} from 'reactstrap';

const Settings = (props) => {
  const setDividerRules = e => (props.setDividerRules(e.target.value))
  const setAdjustmentDividerRule = e => (props.setAdjustmentDividerRule(e.target.value))
  const setAdjustmentMethod = e => (props.setAdjustmentMethod(e.target.value))
  //const adjustmentThreshold = 100 * props.data.election_rules.adjustment_threshold;

  if (!props.capabilitiesLoaded) {
      return <div>Capabilities not loaded</div>;
  }  
  return (
    <Row>
      <Col>
        <h1>Settings</h1>
      </Col>
    </Row>
  )
}

export default Settings;