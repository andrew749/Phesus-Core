let svgIntersections = require('svg-intersections');
let intersect = svgIntersections.intersect;
let shape = svgIntersections.shape;
let _ = require('lodash');

let helpers = {
  getUUID: () => {
    var d = new Date().getTime();
    if (window.performance && typeof window.performance.now === 'function') {
      d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      var r = (d + Math.random()*16)%16 | 0;
      d = Math.floor(d/16);
      return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
  },
  stopEvent: (e) => {
    e.preventDefault();
    e.stopPropagation();
    return false;
  },
  sign: (n) => { return n == 0 ? 0 : n/Math.abs(n) },
  shapeAttrs: new Set(
    'x1,x2,y1,y2,x,y,rx,ry,width,height'
      .split(',')
  ),
  shapeFromElement: (element, inParent) => {
    var props = _.chain(element.attributes)
        .filter((attr) => helpers.shapeAttrs.has(attr.name))
        .map((attr) => {return {name: attr.name, val: parseFloat(attr.value)}})
        .keyBy('name')
        .mapValues((attr) => attr.val)
        .value();
    if (inParent) {
      let match = /translate\((-?\d+\.?\d*) (-?\d+\.?\d*)\)/
        .exec(element.parentNode.getAttribute('transform'));
      console.log(match);
      if (match) {
        props.x += parseFloat(match[1]);
        props.y += parseFloat(match[2]);
      }
    }
    console.log(props);
    return shape(
      element.tagName,
      props
    );
  },
  curveLength: 40,
  anchorsFromElement: (element, inParent) => {
    var x, y, w, h;
    switch (element.tagName.toLowerCase()) {
      case 'rect':
        x = parseFloat(element.getAttribute('x'));
        y = parseFloat(element.getAttribute('y'));
        w = parseFloat(element.getAttribute('width'));
        h = parseFloat(element.getAttribute('height'));
        break;
    }
    var points = [
      {x1: x, y1: y+h/2, x2: x-helpers.curveLength, y2: y+h/2},
      {x1: x+w, y1: y+h/2, x2: x+w+helpers.curveLength, y2: y+h/2},
      {x1: x+w/2, y1: y, x2: x+w/2, y2: y-helpers.curveLength},
      {x1: x+w/2, y1: y+h, x2: x+w/2, y2: y+h+helpers.curveLength}
    ];

    if (inParent) {
      let match = /translate\((-?\d+\.?\d*) (-?\d+\.?\d*)\)/
        .exec(element.parentNode.getAttribute('transform'));
      let dx = parseFloat(match[1]);
      let dy = parseFloat(match[2]);
      return points.map((point) => {
        return {
          x1: point.x1+dx, y1: point.y1+dy,
          x2: point.x2+dx, y2: point.y2+dy
        };
      });
    } else {
      return points;
    }
  },
  permutations: function() {
    return _.reduce(Array.prototype.slice.call(arguments, 1),function(ret,newarr){
        return _.reduce(ret,function(memo,oldi){
            return memo.concat(_.map(newarr,function(newi){
                return oldi.concat(newi);
            }));
        },[]);
    },_.map(arguments[0],function(i){return [i];}));
  }
};

module.exports = helpers;
