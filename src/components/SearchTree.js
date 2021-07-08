import React from "react";
import styles from "./SearchTree.module.css";
import Expanse from "react-expanse";
import { BsChevronRight } from "react-icons/bs";
import { AiOutlineSearch } from "react-icons/ai";
import HrefSvg from "@site/static/img/href.svg";

// 栈。
function Stack(length) {
  const stack = new Array(length);
  let top = 0;
  const push = (item) => (stack[top++] = item);
  const pop = () => stack[--top];
  const peek = () => stack[top - 1];
  const isEmpty = () => top === 0;
  const _look = () => stack;
  return { push, pop, peek, isEmpty, _look };
}

// data 数据结构：
// 树状结构后序遍历得到的列表，每一项为一个 TreeNode
// TreeNode 是一个 object，包含 id, title, parentId, expand
// parentId 为 -1 表示根节点
function Tree(props) {
  const { data, onExpand } = props;
  // Element Stack
  const { push, pop, peek, isEmpty, _look } = Stack(data.length);
  for (let node of data) {
    // console.log(_look());

    if (!isEmpty() && peek().parentId === node.id) {
      // 此节点是父节点，执行子节点合并
      const children = [];
      while (!isEmpty() && peek().parentId === node.id) {
        children.push(pop().element);
      }
      children.reverse();

      const icon = (
        <BsChevronRight
          className={
            node.expand ? `${styles.icon} ${styles.iconExpand}` : styles.icon
          }
        />
      );

      push({
        parentId: node.parentId,
        element: (
          <li key={node.id}>
            <span onClick={() => onExpand(node, !node.expand)}>
              {icon}
              {node.title}
            </span>
            <Expanse show={node.expand}>
              <ul className={`${styles.tree} ${styles.subTree}`}>{children}</ul>
            </Expanse>
          </li>
        ),
      });
    } else {
      push({
        parentId: node.parentId,
        element: (
          <li key={node.id}>
            <span onClick={() => onExpand(node, !node.expand)}>
              {node.title}
            </span>
          </li>
        ),
      });
    }
  }
  const nodes = [];
  while (!isEmpty()) {
    nodes.push(pop().element);
  }
  return <ul className={styles.tree}>{nodes}</ul>;
}

function Search(props) {
  return (
    <div>
      <input {...props} className={styles.search} />
      <AiOutlineSearch className={styles.searchIcon}/>
    </div>
  );
}

// 转换树的数据：压平（后序遍历），增加 id，满足 dataList[node.id] == node
const generateList = (treeData, parentId = -1) => {
  const dataList = [];
  // 逆向前序遍历，最后倒转
  for (let i = treeData.length - 1; i >= 0; i--) {
    const node = treeData[i];
    const { name } = node;
    const id = dataList.length + parentId + 1;
    dataList.push({
      id,
      title: name,
      parentId,
      expand: false,
      leaf: !node.children,
    });
    if (node.children) {
      dataList.push(...generateList(node.children, id));
    }
  }
  // 最后倒转
  if (parentId == -1) {
    const nodeCount = dataList.length;
    dataList.reverse().forEach((node) => {
      node.id = nodeCount - node.id - 1;
      node.parentId = node.parentId == -1 ? -1 : nodeCount - node.parentId - 1;
    });
  }
  return dataList;
};

class SearchTree extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      dataList: generateList(props.data),
      searchValue: "",
    };
  }

  setExpandedNodeIds(expandedNodeIds, autoExpandParent = true) {
    this.setState((state, _) => {
      const { dataList } = state;
      dataList.forEach((node) => {
        node.expand = false;
      });
      for (const node of dataList) {
        // 按照 generateList 给出的数据结构，子节点一定在父节点前面
        node.expand = node.expand || expandedNodeIds.indexOf(node.id) > -1;
        // 因此 autoExpandParent 只需要操作一层
        if (autoExpandParent && node.expand && node.parentId > -1) {
          dataList[node.parentId].expand = true;
        }
      }
      return { dataList };
    });
  }

  onTreeExpand = (data, expanded) => {
    this.setState((state, _) => {
      console.log(state);
      const { dataList } = state;
      dataList[data.id].expand = expanded;
      // 当父节点关闭时，一同关闭子节点
      if (!expanded) {
        for (let i = data.id - 1; i >= 0; i--) {
          if (dataList[i].parentId === data.parentId) {
            break;
          }
          dataList[i].expand = false;
        }
      }
      return { dataList };
    });
  };

  onSearchChange = (e) => {
    const { dataList } = this.state;
    const { value } = e.target;
    this.setState({
      searchValue: value,
    });
    if (value === "") {
      return;
    }
    const expandedNodeIds = dataList
      .map((item) => {
        if (item.title.indexOf(value) > -1) {
          return item.parentId > -1 ? item.parentId : null;
        }
        return null;
      })
      .filter((item, i, self) => item && self.indexOf(item) === i);
    this.setExpandedNodeIds(expandedNodeIds);
  };

  render() {
    const { dataList, searchValue } = this.state;
    const renderNode = (item) => {
      const index = item.title.indexOf(searchValue);
      const beforeStr = item.title.substr(0, index);
      const afterStr = item.title.substr(index + searchValue.length);
      const link = (
        <a
          href={this.props.hrefPrefix + item.title}
          target="_blank"
          style={{
            marginLeft: "0.3rem",
            position: "relative",
            top: "1px",
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <HrefSvg>查看文档</HrefSvg>
        </a>
      );

      return index > -1 ? (
        <span>
          {beforeStr}
          <span className={styles.siteTreeSearchValue}>{searchValue}</span>
          {afterStr}
          {link}
        </span>
      ) : (
        <span>
          {item.title}
          {link}
        </span>
      );
    };
    const isRoot = (node) => node.parentId === -1;
    return (
      <div>
        <Search placeholder="搜索..." onChange={this.onSearchChange} />
        <Tree
          onExpand={this.onTreeExpand}
          data={dataList.map((node) => {
            return {
              ...node,
              title: renderNode(node),
            };
          })}
        />
      </div>
    );
  }
}

export default SearchTree;
