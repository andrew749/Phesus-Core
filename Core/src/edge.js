import React, { } from 'react';

export default function Edge(props) {
  let ARROW_LENGTH = 10;
  return (
    <g className={`edge_${props.id}`}>
      <line
        className='line'
        x1={props.x1}
        y1={props.y1}
        x2={props.x2}
        y2={props.y2}
        stroke='#000'
        strokeWidth='1'
      />
      <polygon
        className='arrow'
        transform={
          `translate(${props.x3} ${props.y3}) ` +
            `rotate(${props.angle})`
        }
        points={`0,0 -${ARROW_LENGTH},5 -${ARROW_LENGTH},-5`}
        fill='#000'
      />
    </g>
  );
}
