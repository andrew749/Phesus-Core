import React, { Component } from 'react';
let ReactDOM = require('react-dom');

export default class Edge extends Component {
  render() {
    return (
      <line
        x1={this.props.x1}
        y1={this.props.y1}
        x2={this.props.x2}
        y2={this.props.y2}
        stroke='#000'
        strokeWidth='1'
      />
    );
  }
}
