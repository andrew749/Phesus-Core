let svgIntersections = require('svg-intersections');
let intersect = svgIntersections.intersect;
let shape = svgIntersections.shape;
let _ = require('lodash');

let h = {
  shapeAttrs: new Set(
    'x1,x2,y1,y2,x,y,rx,ry,width,height'
      .split(',')
  ),
  shapeFromElement: (element, inParent) => {
    var props = _.chain(element.attributes)
        .filter((attr) => h.shapeAttrs.has(attr.name))
        .map((attr) => {return {name: attr.name, val: parseFloat(attr.value)}})
        .keyBy('name')
        .mapValues((attr) => attr.val)
        .value();
    if (inParent) {
      let match = /translate\((\d+\.?\d*) (\d+\.?\d*)\)/
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
  }
};

module.exports = h;
