import React from "react";

const colorTable = [
  "#3BB075",
  "#5EC994",
  "#8C8CD9",
  "#8CB3D9",
  "#8CD98C",
  "#8CD9B3",
  "#8CD9D9",
  "#B03B75",
  "#B38CD9",
  "#B3D98C",
  "#C95E94",
  "#D98C8C",
  "#D98CB3",
  "#D98CD9",
  "#D9B38C",
  "#D9D98C",
];

function StructureDiagram(props) {
  const layers = [];
  for (let i in props.data) {
    const layer = props.data[i];
    const modules = [];
    for (let j in layer) {
      const module = layer[j];
      modules.push(
        <div
          key={j}
          style={{
            float: "left",
            height: "3em",
            width: `${100 / layer.length}%`,
          }}
        >
          <p
            style={{
              margin: `1em ${10 * layer.length}%`,
              width: `${100 - 20 * layer.length}%`,
              textAlign: "center",
              lineHeight: "3em",
              backgroundColor: "#fff8",
              borderRadius: "0.5em",
            }}
          >
            {module}
          </p>
        </div>
      );
    }
    layers.push(
      <div
        key={i}
        style={{
          clear: "both",
          height: "5em",
          backgroundColor: colorTable[i],
          margin: "1em 0",
          borderRadius: "1em",
        }}
      >
        {modules}
      </div>
    );
  }
  return <div>{layers}</div>;
}

export default StructureDiagram;
