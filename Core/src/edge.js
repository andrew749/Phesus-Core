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
    this.update = this.update.bind(this);
    this.arrowLength = 10;
  }
  componentDidMount() {
    this.element = ReactDOM.findDOMNode(this);
    this.line = this.element.querySelector('.line');
    this.arrow = this.element.querySelector('.arrow');
    Dispatcher.on(`${this.props.from}:drag`, this.update);
    Dispatcher.on(`${this.props.to}:drag`, this.update);
    this.update();
  }
  componentWillUnmount() {
    Dispatcher.off(`${this.props.from}:drag`, this.update);
    Dispatcher.off(`${this.props.to}:drag`, this.update);
  }
  update() {
    let from = document.querySelector(`.node_${this.props.from}`);
    let to = document.querySelector(`.node_${this.props.to}`);
    let points = _.minBy(
      Helpers.permutations(
        Helpers.anchorsFromElement(from, true),
        Helpers.anchorsFromElement(to, true)
      ),
      (points) => {
        return Math.abs(
          Math.pow(points[0].x1 - points[1].x1, 2) + 
          Math.pow(points[0].y1 - points[1].y1, 2)
        );
      }
    );
    let angle = Math.atan2(
      points[1].y1 - points[1].y2,
      points[1].x1 - points[1].x2
    ) * 180 / Math.PI;

    let pointTo = _.mapValues(points[1], (v, k, o) => {
      if (o.x1 == o.x2 && k.substr(0, 1) == 'y')
        return v + Helpers.sign(o.y2-o.y1)*this.arrowLength;
      if (o.y1 == o.y2 && k.substr(0, 1) == 'x')
        return v + Helpers.sign(o.x2-o.x1)*this.arrowLength;
      return v;
    }); 
    this.line.setAttribute(
      'd',
      `M ${points[0].x1} ${points[0].y1} ` +
        `C ${points[0].x2} ${points[0].y2}, ` +
        `${pointTo.x2} ${pointTo.y2}, ` +
        `${pointTo.x1} ${pointTo.y1}`
    );
    this.arrow.setAttribute(
      'transform',
      `translate(${points[1].x1} ${points[1].y1}) ` +
        `rotate(${angle})`
    );
  }
  render() {
    return (
      <g className={`edge_${this.props.id}`}>
        <path
          className='line'
          stroke='#000'
          strokeWidth='1'
          fill='transparent'
        />
        <polygon
          className='arrow'
          points={`0,0 -${this.arrowLength},5 -${this.arrowLength},-5`}
          fill='#000'
        />
      </g>
    );
  }
}
