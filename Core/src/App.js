import React, { Component } from 'react';
import Graph from './graph';
import { Menu, Submenu, MenuItem } from './menu';
let Dispatcher = require('./dispatcher');
let Helpers = require('./helpers');
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
      edges: sampleContent.connections,
      viewBox: {},
      menu: {
        addNode: {open: false}
      }
    };
    this.drawAddArrow = this.drawAddArrow.bind(this);
    this.endAddArrow = this.endAddArrow.bind(this);
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
      }))
      .on('menu_toggle', (data) => this.setState((state) => {
        if (data.id && state.menu[data.id]) {
          state.menu[data.id].open = !state.menu[data.id].open;
          (state.menu[data.id].children || []).forEach((child) => {
            if (state.menu[child]) state.menu[child].open = false;
          });
        }
        return state;
      }))
      .on('menu_close_all', () => this.setState((state) => {
        _.each(state.menu, (submenu) => {
          submenu.open = false;
        });
        return state;
      }))
      .on('node_added', (data) => this.setState((state) => {
        var id = '';
        while (id === '' || state.nodes[id]) id = Helpers.getUUID();
        state.nodes[id] = {
          x: state.viewBox.x + state.viewBox.width/2,
          y: state.viewBox.y + state.viewBox.height/2,
          localID: true
        }
      }))
      .on('begin_add_arrow', (data) => {
        this.setState((state) => {
          state.addArrow = data.id;
          return state;
        });
        window.addEventListener('mousemove', this.drawAddArrow);
        window.addEventListener('mouseup', this.endAddArrow);
      })
      .on('end_add_arrow', (data) => {
        this.setState((state) => {
          var id = '';
          while (id === '' || state.edges[id]) id = Helpers.getUUID();
          state.edges[id] = {
            from: state.addArrow,
            to: data.id,
            localID: true
          };
          _.each(state.nodes, (node) => delete node.addArrowSelected);
          delete state.addArrow;
          delete state.addArrowTo;
          return state;
        });
        window.removeEventListener('mousemove', this.drawAddArrow);
        window.removeEventListener('mouseup', this.endAddArrow);
      })
      .on('select_add_arrow', (data) => this.setState((state) => {
        state.nodes[data.id].addArrowSelected = true;
        return state;
      }))
      .on('deselect_add_arrow', (data) => this.setState((state) => {
        delete state.nodes[data.id].addArrowSelected;
        return state;
      }));
  }
  componentDidMount() {
    document.body.addEventListener('click', () => Dispatcher.emit('menu_close_all'));
  }
  endAddArrow(event) {
    this.setState((state) => {
      _.each(state.nodes, (node) => delete node.addArrowSelected);
      delete state.addArrow;
      delete state.addArrowTo;
      return state;
    });
  };
  drawAddArrow(event) {
    this.setState((state) => {
      state.addArrowTo = {
        x: event.clientX,
        y: event.clientY
      };
      return state;
    });
  }
  render() {
    return (
      <div className='app'>
        <Menu title='Phesus'>
          <Submenu name='Add Node' id='addNode' open={this.state.menu.addNode.open}>
            <MenuItem
              name='Regular'
              shortcut='ctrl a'
              event='node_added'
              data={{type: 'regular'}}
             />
          </Submenu>
        </Menu>
        <Graph
          nodes={this.state.nodes}
          edges={this.state.edges}
          x={this.state.viewBox.x}
          y={this.state.viewBox.y}
          width={this.state.viewBox.width}
          height={this.state.viewBox.height}
          addArrow={this.state.addArrow}
          addArrowTo={this.state.addArrowTo}
        />
      </div>
    );
  }
}
