import React, { Component } from 'react';
import Edge from './edge';
import Node from './node';
let ReactDOM = require('react-dom');
let Dispatcher = require('./dispatcher');
let _ = require('lodash');

export default class Graph extends Component {
  componentDidMount() {
    let canvas = ReactDOM.findDOMNode(this);
    let wrapper = canvas.querySelector('.wrapper');
    wrapper.appendChild(wrapper.removeChild(wrapper.querySelector('.nodes')));

    let box = wrapper.getBBox();
    let x = -box.width/2 + canvas.offsetWidth/2 - box.x;
    let y = -box.height/2 + canvas.offsetHeight/2 - box.y;
    wrapper.setAttribute('transform', `translate(${x} ${y})`);
  }
  render() {
    let nodes = _.mapValues(this.props.nodes, (node, id) => {
      return (<Node 
        id={id}
        key={id}
        x={node.x}
        y={node.y}
        content={node.content}
      />);
    });
    let edges = _.mapValues(this.props.edges, (edge, id) => {
      return (<Edge
        id={id}
        key={id}
        from={edge.from}
        to={edge.to}
        x1={this.props.nodes[edge.from].x}
        y1={this.props.nodes[edge.from].y}
        x2={this.props.nodes[edge.to].x}
        y2={this.props.nodes[edge.to].y}
      />);
    });
    return(
      <svg className='canvas'>
        <g className='wrapper'>
          <g className='nodes'>
            {_.values(nodes)}
          </g>
          <g className='edges'>
            {_.values(edges)}
          </g>
        </g>
      </svg>
    );
  }
}
