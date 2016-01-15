import React, { Component } from 'react';
import Graph from './graph';
let _ = require('lodash');

let sampleContent = {
  nodes: {
    "1": {
      x: 0,
      y: 0,
      content: {title: "Hello, world"}
    }
  },
  connections: {}
};

export default class App extends Component {
  render() {
    let nodes = _.map(sampleContent.nodes, (node, id) => {
     return (<Node 
        id={id}
        x={node.x}
        y={node.y}
        content={node.content}
      />);
    });
    //let edges = _.map(sampleContent.connections, (edge, id) => {
       //return (<Edge
        ///>);
      //});

    return (
      <h1>Pheseus</h1>
      <Graph>
        {nodes}
      </Graph>
    );
  }
}
