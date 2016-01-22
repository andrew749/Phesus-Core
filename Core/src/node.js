import React, { Component } from 'react';
import InnerHTML from './innerhtml';
let Dispatcher = require('./dispatcher');
let _ = require('lodash');
let ReactDOM = require('react-dom');

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
    //let autosized = this.element.querySelector('.autosized');
    //let content = this.element.querySelector('.content');

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
    event.preventDefault();
    return false;
  }
  endDrag(event) {
    this.element.classList.remove('dragging');
    window.removeEventListener('mousemove', this.drag);
    window.removeEventListener('mouseup', this.endDrag);
    this.element.addEventListener('mousedown', this.beginDrag);
    this.moveTo(
      this.props.x + event.clientX - this.initialX,
      this.props.y + event.clientY - this.initialY
    );
  }
  drag(event) {
    this.moveTo(
      this.props.x + event.clientX - this.initialX,
      this.props.y + event.clientY - this.initialY
    );
    this.initialX = event.clientX;
    this.initialY = event.clientY;
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
              className: `default node_${node.id}`
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
      <g transform={this.getTransform(this.props.x, this.props.y)}>
        {Node.SVG_FROM(Node.SHAPE_FROM(this.props))}
        <InnerHTML content={this.props.content} />
      </g>
    );
  }
}
