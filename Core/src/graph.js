import React, { Component } from 'react';
import Edge from './edge';
import Node from './node';
let ReactDOM = require('react-dom');
let Dispatcher = require('./dispatcher');
let _ = require('lodash');
let svgIntersections = require('svg-intersections');
let intersect = svgIntersections.intersect;
let shape = svgIntersections.shape;
let Helpers = require('./helpers');

export default class Graph extends Component {
  static ZOOM_FACTOR = 0.95;
  constructor(props) {
    super(_.defaults(props, {
      nodes: [],
      edges: []
    }));
    this.beginDrag = this.beginDrag.bind(this);
    this.endDrag = this.endDrag.bind(this);
    this.drag = this.drag.bind(this);
    this.zoom = this.zoom.bind(this);
  }
  componentDidMount() {
    this.canvas = ReactDOM.findDOMNode(this);
    this.canvas.addEventListener('mousedown', this.beginDrag);
    this.canvas.addEventListener('wheel', this.zoom);
    let wrapper = this.canvas.querySelector('.wrapper');
    wrapper.appendChild(wrapper.removeChild(wrapper.querySelector('.nodes')));

    if (!this.hasViewBox()) {
      let box = wrapper.getBBox();
      Dispatcher.emit('viewBox_changed', {
        changed: {
          x: box.x - this.canvas.offsetWidth/2 + box.width/2,
          y: box.y - this.canvas.offsetHeight/2 + box.height/2,
          width: this.canvas.offsetWidth,
          height: this.canvas.offsetHeight
        }
      });
    }
  }
  componentWillUnmount() {
    this.canvas.removeEventListener('mousedown', this.beginDrag);
    this.canvas.removeEventListener('wheel', this.zoom);
    window.removeEventListener('mouseup', this.endDrag);
    window.removeEventListener('mousemove', this.drag);
  }
  beginDrag(event) {
    this.canvas.classList.add('grabbing');
    this.canvas.removeEventListener('mousedown', this.beginDrag);
    window.addEventListener('mouseup', this.endDrag);
    window.addEventListener('mousemove', this.drag);
    this.initialX = event.clientX;
    this.initialY = event.clientY;
    return Helpers.stopEvent(event);
  }
  endDrag(event) {
    this.canvas.classList.remove('grabbing');
    window.removeEventListener('mousemove', this.drag);
    window.removeEventListener('mouseup', this.endDrag);
    this.canvas.addEventListener('mousedown', this.beginDrag);
    this.moveTo(
      this.props.x - event.clientX + this.initialX,
      this.props.y - event.clientY + this.initialY
    );
    return Helpers.stopEvent(event);
  }
  drag(event) {
    this.moveTo(
      this.props.x - event.clientX + this.initialX,
      this.props.y - event.clientY + this.initialY
    );
    this.initialX = event.clientX;
    this.initialY = event.clientY;
    return Helpers.stopEvent(event);
  }
  moveTo(x, y) {
    Dispatcher.emit('viewBox_changed', {
      changed: {x, y}
    });
  }
  zoom(event) {
    let direction = Helpers.sign(event.deltaY || event.deltaX);
    if (direction == 0) return;

    let deltaX = Math.pow(Graph.ZOOM_FACTOR, direction) * this.props.width;
    let deltaY = Math.pow(Graph.ZOOM_FACTOR, direction) * this.props.height;
    Dispatcher.emit('viewBox_changed', {
      changed: {
        x: this.props.x + (this.props.width - deltaX)/2,
        y: this.props.y + (this.props.height - deltaY)/2,
        width: deltaX,
        height: deltaY
      }
    });
    Helpers.stopEvent(event);
  }
  hasViewBox() {
    return (['x', 'y', 'width', 'height'].every((k) => this.props[k] !== undefined));
  }
  getViewBox() {
    if (this.hasViewBox()) {
      return `${this.props.x} ${this.props.y} ${this.props.width} ${this.props.height}`;
    } else {
      return undefined;
    }
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
        x3={intersection.points.length ? intersection.points[0].x : undefined}
        y3={intersection.points.length ? intersection.points[0].y : undefined}
        angle={Math.atan2(
          this.props.nodes[edge.to].y - this.props.nodes[edge.from].y,
          this.props.nodes[edge.to].x - this.props.nodes[edge.from].x
        ) * 180 / Math.PI}
      />);
    });
    return(
      <svg className='canvas' viewBox={this.getViewBox()}>
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
