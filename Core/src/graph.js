import React, { Component } from 'react';
let ReactDOM = require('react-dom');

export default class Graph extends Component {
  componentDidMount() {
    let canvas = ReactDOM.findDOMNode(this);
    let wrapper = canvas.querySelector('.wrapper');

    let box = wrapper.getBBox();
    let x = -box.width/2 + canvas.offsetWidth/2 - box.x;
    let y = -box.height/2 + canvas.offsetHeight/2 - box.y;
    wrapper.setAttribute('transform', `translate(${x} ${y})`);
  }
  render() {
    return(
      <svg className='canvas'>
        <g className='wrapper'>
          {this.props.children}
        </g>
      </svg>
    );
  }
}
