import React, { Component } from 'react';
import InnerHTML from './innerhtml';
let Dispatcher = require('./dispatcher');
let _ = require('lodash');
let ReactDOM = require('react-dom');

export default class Node extends Component {
  constructor(props) {
    super(props);
    this.beginDrag = this.beginDrag.bind(this);
    this.endDrag = this.endDrag.bind(this);
    this.drag = this.drag.bind(this);
  }
  componentDidMount() {
    this.element = ReactDOM.findDOMNode(this);

    var autosized = this.element.querySelector('.autosized');
    let content = this.element.querySelector('.content');

    let box = content.getBBox();
    let padding = 10;
    let w = box.width + 2*padding;
    let h = box.height + 2*padding;
    autosized.setAttribute('width', w);
    autosized.setAttribute('height', h);
    autosized.setAttribute('x', -w/2);
    autosized.setAttribute('y', -h/2);

    this.element.addEventListener('mousedown', this.beginDrag);
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
  }
  endDrag(event) {
    this.element.classList.remove('dragging');
    window.removeEventListener('mousemove', this.drag);
    window.removeEventListener('mouseup', this.endDrag);
    this.element.addEventListener('mousedown', this.beginDrag);
    Dispatcher.emit(`node_changed`, {
      id: this.props.id,
      changed: {
        x: this.props.x + event.clientX - this.initialX,
        y: this.props.y + event.clientY - this.initialY
      }
    });
  }
  drag(event) {
    let newX = this.props.x + event.clientX - this.initialX; 
    let newY = this.props.y + event.clientY - this.initialY;
    this.element.setAttribute('transform', this.getTransform(newX, newY));
    Dispatcher.emit(`${this.props.id}:drag`, {
      x: newX,
      y: newY
    });
    event.preventDefault();
    return false;
  }
  getTransform(x, y) {
    return `translate(${x} ${y})`;
  }
  svgElement() {
    switch (this.props.type) {
      default:
        return (
          <rect x='0' y='0' rx='5' ry='5'
          className={`default autosized node_${this.props.id}`}>
          </rect>
        );
    }
  }
  render() {
    return(
      <g transform={this.getTransform(this.props.x, this.props.y)}>
        {this.svgElement()}
        <InnerHTML content={this.props.content} />
      </g>
    );
  }
}
