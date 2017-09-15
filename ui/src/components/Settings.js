import React, { Component } from 'react';
import {
  Row,
  Col,
  Form,
  FormGroup,
  Label,
  Input,
  FormText
} from 'reactstrap';

const Settings = (props) => {

  //const adjustmentThreshold = 100 * props.data.election_rules.adjustment_threshold;
  const adjustmentMethods = Object.keys(props.adjustmentMethods).map(k => {
    return (
      <option>{props.adjustmentMethods[k]}</option>
    )
  })
  const dividerRules = Object.keys(props.dividerRules).map(k => {
    return (
      <option>{props.dividerRules[k]}</option>
    )
  })  
  return (
    <Row>
      <Col>
        <h1>Settings</h1>
        <Form>
        <FormGroup>
          <Label for="exampleSelect">Adjustment methods</Label>
          <Input type="select" name="select" id="exampleSelect">
            {adjustmentMethods}
          </Input>
        </FormGroup>
        <FormGroup>
          <Label for="exampleSelect">Divider rules</Label>
          <Input type="select" name="select" id="exampleSelect">
            {dividerRules}
          </Input>
        </FormGroup>
        </Form>
      </Col>
    </Row>
  )
}

export default Settings;