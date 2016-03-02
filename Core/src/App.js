import React, { Component } from 'react';
import Graph from './graph';
import { Menu, Submenu, MenuItem, SideBar, SideBarEntry } from './menu';
let Dispatcher = require('./dispatcher');
let Helpers = require('./helpers');
let _ = require('lodash');
let update = require('react-addons-update');

export default class App extends Component {
  constructor() {
    super();
    this.state = {
      nodes: {},
      edges: {},
      viewBox: {},
      menu: {
        addNode: {open: false}
      }
    };
    this.drawAddArrow = this.drawAddArrow.bind(this);
    this.endAddArrow = this.endAddArrow.bind(this);
    $.get("/getProjects", function(data){
      this.setState((state) => {
        let tempData = [];
        for (let x of JSON.parse(data)) {
          tempData.push({id:x, name:"test " + x});
        }
        state.projectIds = tempData;
        state.clickedId = tempData[0].id;
        $.get("/getProject/" + tempData[0].id , function(dataProject){
           let response = JSON.parse(dataProject);
           state.nodes = response.nodes || {};
           state.edges = response.connections || {};
           this.setState(state);
        }.bind(this));
        return state;
      });
    }.bind(this));

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
        let x_pos = state.viewBox.x + state.viewBox.width/2;
        let y_pos = state.viewBox.y + state.viewBox.height/2;
        state.nodes[id] = {
          x: x_pos,
          y: y_pos,
          localID: true
        }
        $.get(`/createNode/${state.clickedId}/${x_pos}/${y_pos}`, function (data){
            let response = JSON.parse(data);
            console.log(response);
            //set the node to the server provided id.
        });
        return state;
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
          $.get(`/createConnection/${state.clickedId}/${state.addArrow}/${data.id}`, function(data){
            let response = JSON.parse(data);
            console.log(response);
            //set the node id in the editor from a temporary id to the server provided id
          });
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
      }))
      .on('sidemenu_click', (data) => this.setState((state) => {
        state.clickedId = data;
        $.get("/getProject/" + data , function(dataProject){
           let response = JSON.parse(dataProject);
           state.nodes = response.nodes || {};
           state.edges = response.connections || {};
           state.clickedId = data;
           Dispatcher.emit('loaded_project', state);
        });
        return state;
      })).on('loaded_project', (data) => this.setState((state) => {
        state.nodes = data.nodes;
        state.edges = data.edges;
        state.clickedId = data.clickedId;
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
        </Menu >
        <div className="content-wrapper">
          <SideBar clickedId={this.state.clickedId} data={(this.state.projectIds) ? this.state.projectIds : []}/>
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
      </div>
    );
  }
}
