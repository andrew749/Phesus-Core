import React, { Component } from 'react';
import Edge from './edge';
import Node from './node';
let ReactDOM = require('react-dom');
let Dispatcher = require('./dispatcher');
let _ = require('lodash');
let svgIntersections = require('svg-intersections');
let intersect = svgIntersections.intersect;
let shape = svgIntersections.shape;

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
        width={node.width || 0}
        height={node.height || 0}
        content={node.content}
      />);
    });
    let edges = _.mapValues(this.props.edges, (edge, id) => {
      let intersection = intersect(
        shape('line', {
          x1: this.props.nodes[edge.from].x,
          y1: this.props.nodes[edge.from].y,
          x2: this.props.nodes[edge.to].x,
          y2: this.props.nodes[edge.to].y
        }),
        shape(...Node.ABSOLUTE(
          this.props.nodes[edge.to],
          Node.SHAPE_FROM(this.props.nodes[edge.to])
        ))
      );
      return (<Edge
        id={id}
        key={id}
        from={edge.from}
        to={edge.to}
        x1={this.props.nodes[edge.from].x}
        y1={this.props.nodes[edge.from].y}
        x2={this.props.nodes[edge.to].x}
        y2={this.props.nodes[edge.to].y}
        x3={intersection.points.length ? intersection.points[0].x : 0}
        y3={intersection.points.length ? intersection.points[0].y : 0}
        angle={Math.atan2(
          this.props.nodes[edge.to].y - this.props.nodes[edge.from].y,
          this.props.nodes[edge.to].x - this.props.nodes[edge.from].x
        ) * 180 / Math.PI}
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
