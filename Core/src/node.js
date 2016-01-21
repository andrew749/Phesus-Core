import React, { Component } from 'react';
import InnerHTML from './innerhtml';
let Dispatcher = require('./dispatcher');
let _ = require('lodash');
let ReactDOM = require('react-dom');

export default class Node extends Component {
  componentDidMount() {
    let element = ReactDOM.findDOMNode(this);

    var autosized = element.querySelector('.autosized');
    let content = element.querySelector('.content');

    let box = content.getBBox();
    let padding = 10;
    let w = box.width + 2*padding;
    let h = box.height + 2*padding;
    console.log(w, h);
    autosized.setAttribute('width', w);
    autosized.setAttribute('height', h);
    autosized.setAttribute('x', -w/2);
    autosized.setAttribute('y', -h/2);
  }
  svgElement() {
    switch (this.props.type) {
      default:
        return (
          <rect x='0' y='0' rx='5' ry='5'
          className='default autosized'>
          </rect>
        );
    }
  }
  render() {
    return(
      <g transform={`translate(${this.props.x} ${this.props.y})`}>
        {this.svgElement()}
        <InnerHTML content={this.props.content} />
      </g>
    );
  }
}
