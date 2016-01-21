import React, { Component } from 'react';
let ReactDOM = require('react-dom');
let Dispatcher = require('./dispatcher');
let svgIntersections = require('svg-intersections');
let intersect = svgIntersections.intersect;
let shape = svgIntersections.shape;
let Helpers = require('./helpers');

export default class Edge extends Component {
  constructor(props) {
    super(props);
    this.updateFrom = this.updateFrom.bind(this);
    this.updateTo = this.updateTo.bind(this);
  }
  componentDidMount() {
    this.element = ReactDOM.findDOMNode(this);
    this.line = this.element.querySelector('.line');
    this.arrow = this.element.querySelector('.arrow');
    Dispatcher.on(`${this.props.from}:drag`, this.updateFrom);
    Dispatcher.on(`${this.props.to}:drag`, this.updateTo);
    this.updateArrow();
  }
  componentWillUnmount() {
    Dispatcher.off(`${this.props.from}:drag`, this.updateFrom);
    Dispatcher.off(`${this.props.to}:drag`, this.updateTo);
  }
  updateFrom(data) {
    this.line.setAttribute('x1', data.x);
    this.line.setAttribute('y1', data.y);
    this.updateArrow();
  }
  updateTo(data) {
    this.line.setAttribute('x2', data.x);
    this.line.setAttribute('y2', data.y);
    this.updateArrow();
  }
  updateArrow() {
    let intersection = intersect(
      Helpers.shapeFromElement(this.line),
      Helpers.shapeFromElement(
        document.querySelector(`.node_${this.props.to}`), true
      )
    );
    console.log(intersection);
    let angle = Math.atan2(
      parseFloat(this.line.getAttribute('y2'))
        - parseFloat(this.line.getAttribute('y1')),
      parseFloat(this.line.getAttribute('x2'))
      - parseFloat(this.line.getAttribute('x1'))
    ) * 180 / Math.PI;
    this.arrow.setAttribute(
      'transform',
      `translate(${intersection.points[0].x} ${intersection.points[0].y}) ` +
        `rotate(${angle})`
    );
  }
  render() {
    return (
      <g className={`edge_${this.props.id}`}>
        <line
          className='line'
          x1={this.props.x1}
          y1={this.props.y1}
          x2={this.props.x2}
          y2={this.props.y2}
          stroke='#000'
          strokeWidth='1'
        />
        <polygon
          className='arrow'
          points="0,0 -10,5 -10,-5"
          fill='#000'
        />
      </g>
    );
  }
}
