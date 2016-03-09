import React, { Component } from 'react';
import Graph from './graph';
import { Menu, Submenu, MenuItem, SideBar, SideBarEntry } from './menu';
let Dispatcher = require('./dispatcher');
let Helpers = require('./helpers');
let _ = require('lodash');
let update = require('react-addons-update');


export default class App extends Component {
  static post(url, data, callback) {
    $.ajax({
      type: "POST",
      url: url,
      // The key needs to match your method's input parameter (case-sensitive).
      data: JSON.stringify(data),
      contentType: "application/json; charset=utf-8",
      success: callback
    });
  }

  constructor() {
    super();
    // the initial state
    this.state = {
      nodes: {},
      edges: {},
      viewBox: {},
      menu: {
        addNode: {open: false},
      },
      open: false
    };
    //set the environment
    this.drawAddArrow = this.drawAddArrow.bind(this);
    this.endAddArrow = this.endAddArrow.bind(this);

    //initial query for a users projects
    $.get("/getProjects", function(data){
      //update the ui with the projects
      this.setState((state) => {
        let tempData = [];
        for (let x of JSON.parse(data)) {
          tempData.push({id:x, name:"test " + x});
        }
        state.projectIds = tempData;
        state.clickedId = tempData[0].id;

        //secondary query to get the data for each project
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
      .on('node_did_finish_moving', (data) => {
          let tempNode = this.state.nodes[data.id];
          App.post(`/updateNode/${this.state.clickedId}/${data.id}/${tempNode.x}/${tempNode.y}/${tempNode.type}`, {"content": "hello"}, (data) => this.setState((state) => {
            let id = data.id;
            if (state.nodes[id]) {
              let response = JSON.parse(data);
              //set the node to the server provided id.
              state.nodes[response] = state.nodes[id];
              delete state.nodes[id];
            }
            return state;
            })
          );
      })
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
        App.post(`/createNode/${state.clickedId}/${x_pos}/${y_pos}`, {"content":"test"}, (data) => {
            if (state.nodes[id]) {
              let response = JSON.parse(data);
              //set the node to the server provided id.
              state.nodes[response] = state.nodes[id];
              delete state.nodes[id];
              this.setState(state);
            }
        })
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
          $.post(`/createConnection/${state.clickedId}/${state.addArrow}/${data.id}`, function(data){
            if (state.edges[id]) {
            let response = JSON.parse(data);
            //set the node id in the editor from a temporary id to the server provided id
            state.edges[response] = state.edges[id];
            delete state.edges[id];
            this.setState(state);
            }
          });

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
      })).on('side_menu_toggle', (data) => this.setState((state) => {
        let sidebar = document.getElementById("sidebar");
        let menuIcon = document.getElementById("menu-icon");
        let open = state.open;
        menuIcon.className = `fa fa-bars ${(!open) ? "menu-icon-closed" : "menu-icon-open"}`;
        sidebar.className = `sidebar ${(!open) ? "sidebar-closed" : "sidebar-open"}`;
        state.open = !open;
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
        <div className='topBar'>
          <i id="menu-icon" className="fa fa-bars open-menu-icon" onClick={toggleSideMenu}></i>
          <Menu title='Phesus'>
            <Submenu name='Add Node' id='addNode' open={this.state.menu.addNode.open}>
              <i class="fa-plus-circle fa"/>
              <MenuItem
                name='Regular'
                shortcut='ctrl a'
                event='node_added'
                data={{type: 'regular'}}
               />
            </Submenu>
          </Menu >
        </div>
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

function toggleSideMenu() {
  Dispatcher.emit('side_menu_toggle',{});
}


