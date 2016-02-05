import React, { Component } from 'react';
import InnerHTML from './innerhtml';
let Dispatcher = require('./dispatcher');
let _ = require('lodash');
let ReactDOM = require('react-dom');
let Helpers = require('./helpers');

export default class Node extends Component {
  static defaultProps = {
    ...Component.defaultProps,
    width: 0,
    height: 0
  };
  static PADDING = 10;
  constructor(props) {
    super(props);
    this.beginDrag = this.beginDrag.bind(this);
    this.endDrag = this.endDrag.bind(this);
    this.drag = this.drag.bind(this);
  }
  componentDidMount() {
    this.element = ReactDOM.findDOMNode(this);
    this.element.addEventListener('mousedown', this.beginDrag);

    if (this.props.width === 0 && this.props.height === 0) {
      let box = this.element.querySelector('.content').getBBox();
      Dispatcher.emit(`node_changed`, {
        id: this.props.id,
        changed: {
          width: box.width + 2*Node.PADDING,
          height: box.height + 2*Node.PADDING
        }
      });
    }
  }
  componentWillUnmount() {
    this.element.removeEventListener('mousedown', this.beginDrag);
    window.removeEventListener('mouseup', this.endDrag);
    window.removeEventListener('mousemove', this.drag);
  }
  beginDrag(event) {
    this.element.classList.add('dragging');
    this.element.removeEventListener('mousedown', this.beginDrag);
    window.addEventListener('mouseup', this.endDrag);
    window.addEventListener('mousemove', this.drag);
    this.initialX = event.clientX;
    this.initialY = event.clientY;
    return Helpers.stopEvent(event);
  }
  endDrag(event) {
    this.element.classList.remove('dragging');
    window.removeEventListener('mousemove', this.drag);
    window.removeEventListener('mouseup', this.endDrag);
    this.element.addEventListener('mousedown', this.beginDrag);
    this.moveTo(
      this.props.x + (event.clientX - this.initialX)*(this.props.scaleX || 1),
      this.props.y + (event.clientY - this.initialY)*(this.props.scaleY || 1)
    );
    return Helpers.stopEvent(event);
  }
  drag(event) {
    this.moveTo(
      this.props.x + (event.clientX - this.initialX)*(this.props.scaleX || 1),
      this.props.y + (event.clientY - this.initialY)*(this.props.scaleY || 1)
    );
    this.initialX = event.clientX;
    this.initialY = event.clientY;
    return Helpers.stopEvent(event);
  }
  moveTo(x, y) {
    Dispatcher.emit(`node_changed`, {
      id: this.props.id,
      changed: {x, y}
    });
  }
  getTransform(x, y) {
    return `translate(${x} ${y})`;
  }
  static SHAPE_FROM(node) {
    switch (node.type) {
      default:
        return (
          [
            'rect',
            {
              x: -node.width/2,
              y: -node.height/2,
              width: node.width,
              height: node.height,
              rx: 5,
              ry: 5,
              className: `bg default node_${node.id}`
            }
          ]
        );
    }
  }
  static ABSOLUTE(node, shape) {
    shape[1].x += node.x;
    shape[1].y += node.y;
    return shape;
  }
  static SVG_FROM(shape) {
    switch (shape[0]) {
      case ('rect'):
        return (<rect {...shape[1]} />);
      default:
        return (<g {...shape[1]} />);
    }
  }
  render() {
    return(
      <g className='node' transform={this.getTransform(this.props.x, this.props.y)}>
        <g className='add_arrow' transform={this.getTransform(0, (this.props.height || 0)/2 + 20)}>
          <rect x={-30} y={-25} width={60} height={40} />
          <circle r={15} />
          <line x1={0} y1={-10} x2={0} y2={1} stroke='#000' strokeWidth={1} />
          <polygon
            points='0,10 -5,0 5,0'
            fill='#000'
          />
        </g>
        {Node.SVG_FROM(Node.SHAPE_FROM(this.props))}
        <InnerHTML content={this.props.content || {}} />
      </g>
    );
  }
}
