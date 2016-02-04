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
