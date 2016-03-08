import React, { Component } from 'react';
let _ = require('lodash');
let Dispatcher = require('./dispatcher');
let Helpers = require('./helpers');

export function Menu(props) {
  return (
    <div className='menu'>
      {
        props.title ?
          (
            <div className='menu_item title'>
              <div className='label'>
                {props.title}
              </div>
            </div>
          ) :
          undefined
      }
      {props.children}
    </div>
  );
}

export class Submenu extends Component {
  constructor(props) {
    super(props);
    this.toggleOpen = this.toggleOpen.bind(this);
  }
  toggleOpen(event) {
    Dispatcher.emit(`menu_toggle`, {id: this.props.id});
    if (event) return Helpers.stopEvent(event);
  }
  render() {
    return (
      <div className={`menu_item ${this.props.open ? 'open' : ''}`}>
        <div className='label' onClick={this.toggleOpen}>
          {this.props.name}
        </div>
        <Menu>
          {this.props.children}
        </Menu>
      </div>
    );
  }
}

export class MenuItem extends Component {
  constructor(props) {
    super(props);
    this.emitEvent = this.emitEvent.bind(this);
  }
  emitEvent(event) {
    Dispatcher.emit('menu_close_all');
    Dispatcher.emit(this.props.event, this.props.data);
    if (event) return Helpers.stopEvent(event);
  }
  render() {
    return (
      <div className='menu_item'>
        <div className='label' onClick={this.emitEvent}>
          {this.props.name}
        </div>
      </div>
    );
  }
}

export class SideBarEntry extends Component {
  constructor(props) {
    super(props);
    this.clickItem = this.clickItem.bind(this);
  }

  clickItem() {
    Dispatcher.emit('sidemenu_click', this.props.id);
  }

  render() {
    return (
      <div onClick={this.clickItem} className={this.props.enabled ?'sidebarEntry sidebarEntrySelected' : 'sidebarEntry'}>
        {this.props.name}
      </div>
    );
  }
}

export class SideBar extends Component {
    render(){
    return (
      <div id="sidebar" className='sidebar'>
      {this.props.data.map((data) => {
        if (this.props.clickedId == data.id)
          return <SideBarEntry id={data.id} enabled={true} name={data.name} key={data.name} />;
        else
          return <SideBarEntry id={data.id} enabled={false} name={data.name} />;
      })}
      </div>
    );
  }

}
