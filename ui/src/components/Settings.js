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
  if (Object.keys(props.electionRules).length === 0) {
    console.log('empty props')
    return <p>Loading capabilities</p>
  }  
  //const adjustmentThreshold = 100 * props.data.election_rules.adjustment_threshold;
  const primaryDividerRule = Object.keys(props.dividerRules).map((k, i) => {
    const selected = ((k === props.electionRules.primary_divider) ? 'selected' : '')
    return (
      <option key={i} selected={true} value={k}>{props.dividerRules[k]}</option>
    )
  })
  const adjustmentDividerRule = Object.keys(props.dividerRules).map((k, i) => {
    const selected = ((k === props.electionRules.adjustment_divider) ? 'selected' : '')
    return (
      <option key={i} selected value={k}>{props.dividerRules[k]}</option>
    )
  })
  const adjustmentMethods = Object.keys(props.adjustmentMethods).map((k, i) => {
    const selected = ((k === props.electionRules.adjustment_method) ? 'selected' : '')
    return (
      <option key={i} selected value={k}>{props.adjustmentMethods[k]}</option>
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
            {primaryDividerRule}
          </Input>
        </FormGroup>
        <FormGroup>
          <Label for="exampleSelect">Primary divider rule</Label>
          <Input type="select" name="select" id="exampleSelect">
            {adjustmentDividerRule}
          </Input>
        </FormGroup>
        <FormGroup>
          <Label for="exampleSelect">Adjustment method</Label>
          <Input type="select" name="select" id="exampleSelect">
            {adjustmentMethods}
          </Input>
        </FormGroup>
        </Form>
      </Col>
    </Row>
  )
}

export default Settings;