import React, { Component } from 'react';
import Graph from './graph';
let Dispatcher = require('./dispatcher');
let _ = require('lodash');
let update = require('react-addons-update');

let sampleContent = {
  nodes: {
    '1': {
      x: 0,
      y: 0,
      content: {title: 'Hello, world'}
    },
    '2': {
      x: 200,
      y: -30,
      content: {title: 'How\'s it going?'}
    },
    '3': {
      x: 130,
      y: 160,
      content: {title: 'broooooo'}
    }
  },
  connections: {
    '1': {
      from: '1',
      to: '2'
    },
    '2': {
      from: '2',
      to: '3'
    }
  }
};

export default class App extends Component {
  constructor() {
    super();
    this.state = {
      nodes: sampleContent.nodes,
      edges: sampleContent.connections,
      viewBox: {}
    };
    Dispatcher
      .on('node_changed', (data) => this.setState((state) => {
        for (var key in data.changed) {
          state.nodes[data.id][key] = data.changed[key];
        }
        return state;
      }))
      .on('edge_changed', (data) => this.setState((state) => {
        for (var key in data.changed) {
          state.edges[data.id][key] = data.changed[key];
        }
        return state;
      }))
      .on('viewBox_changed', (data) => this.setState((state) => {
        for (var key in data.changed) {
          state.viewBox[key] = data.changed[key];
        }
        return state;
      }));
  }
  render() {
    return (
      <div className='app'>
        <h1>Phesus</h1>
        <Graph
          nodes={this.state.nodes}
          edges={this.state.edges}
          x={this.state.viewBox.x}
          y={this.state.viewBox.y}
          width={this.state.viewBox.width}
          height={this.state.viewBox.height}
        />
      </div>
    );
  }
}
