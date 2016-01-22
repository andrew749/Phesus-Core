import React, { Component } from 'react';
import Graph from './graph';
let Dispatcher = require('./dispatcher');
let _ = require('lodash');

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
      edges: sampleContent.connections
    };
  }
  componentDidMount() {
    Dispatcher
      .on('node_changed', (data) => this.setState({
        nodes: _.merge({}, this.state.nodes, {[data.id]: data.changed})
      }))
      .on('edge_changed', (data) => this.setState({
        edges: _.merge({}, this.state.edges, {[data.id]: data.changed})
      }));
  }
  render() {
    return (
      <div className='app'>
        <h1>Phesus</h1>
        <Graph nodes={this.state.nodes} edges={this.state.edges} />
      </div>
    );
  }
}
