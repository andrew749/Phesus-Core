var listeners = {};

let getListeners = function(event) {
  if (!listeners[event]) {
    listeners[event] = [];
  }
  return listeners[event];
};

module.exports = {
  on: function(event, callback) {
    getListeners(event).push(callback);
    return this;
  },
  off: function(event, callback) {
    listeners[event] = getListeners(event).filter((c) => c != callback);
    return this;
  },
  clear: function(event) {
    delete listeners[event];
    return this;
  },
  emit: function(event, data) {
    getListeners(event).forEach((c) => c(data || {}));
    return this;
  }
};
