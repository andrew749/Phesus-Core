import React, { Component } from 'react';
let ReactDOM = require('react-dom');

export default class InnerHTML extends Component {
  render() {
    return (
      <text className={this.props.content.title ? 'content' : 'content empty'}
      x='0' y='0' textAnchor='middle' dy='0.3em'>
        {this.props.content.title || 'Add content here'}
      </text>
    );
  }
}
