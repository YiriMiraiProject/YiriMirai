import React, { PureComponent } from "react";
import { Treebeard } from "react-treebeard";

class Tree extends PureComponent {
  constructor(props) {
    super(props);
    const data = this.props.data;
    this.state = { data };
    this.onToggle = this.onToggle.bind(this);
  }

  onToggle(node, toggled) {
    const { cursor, data } = this.state;
    if (cursor) {
      this.setState(() => ({ cursor, active: false }));
    }
    node.active = true;
    if (node.children) {
      node.toggled = toggled;
    }
    this.setState(() => ({ cursor: node, data: Object.assign({}, data) }));
  }

  render() {
    const { data } = this.state;
    return <Treebeard data={data} onToggle={this.onToggle} />;
  }
}

export default Tree;
