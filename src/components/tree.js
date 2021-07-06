import React from "react";
import "antd/dist/antd.css";
import { Tree, Input } from "antd";
import styles from "./tree.module.css";
import HrefSvg from "@site/static/img/href.svg";

const { Search } = Input;

// 转换树的数据，增加 key
const generateData = (treeData, keyPrefix = "0") => {
  const data = [];
  for (let i in treeData) {
    const node = treeData[i];
    const { name } = node;
    const key = `${keyPrefix}-${i}`;
    const nodeNew = {
      title: name,
      key,
    };
    if (node.children) {
      nodeNew.children = generateData(node.children, key);
    }
    data.push(nodeNew);
  }
  return data;
};

// 压平树，得到节点列表
const generateList = (data) => {
  const dataList = [];
  for (let i in data) {
    const node = data[i];
    const { key, title } = node;
    dataList.push({ key, title });
    if (node.children) {
      dataList.push(...generateList(node.children));
    }
  }
  return dataList;
};

// 获取父节点
const getParentKey = (key, tree) => {
  let parentKey;
  for (let node of tree) {
    if (node.children) {
      if (node.children.some((item) => item.key === key)) {
        parentKey = node.key;
      } else if (getParentKey(key, node.children)) {
        parentKey = getParentKey(key, node.children);
      }
    }
  }
  return parentKey;
};

class SearchTree extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      expandedKeys: [],
      searchValue: "",
      autoExpandParent: true,
    };
    this.gData = generateData(props.data);
    this.dataList = generateList(this.gData);
  }

  onTreeExpand = (expandedKeys) => {
    this.setState({
      expandedKeys,
      autoExpandParent: false,
    });
  };

  onSearchChange = (e) => {
    const { value } = e.target;
    const expandedKeys = this.dataList
      .map((item) => {
        if (item.title.indexOf(value) > -1) {
          return getParentKey(item.key, this.gData);
        }
        return null;
      })
      .filter((item, i, self) => item && self.indexOf(item) === i);
    this.setState({
      expandedKeys,
      searchValue: value,
      autoExpandParent: true,
    });
  };

  componentWillUnmount() {
    // 解决 ant-design 可能存在的内存泄漏问题
    this.setState = (..._) => {};
  }

  render() {
    const { searchValue, expandedKeys, autoExpandParent } = this.state;
    const loop = (data) =>
      data.map((item) => {
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
          >
            <HrefSvg>查看文档</HrefSvg>
          </a>
        );
        const title =
          index > -1 ? (
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
        if (item.children) {
          return { title, key: item.key, children: loop(item.children) };
        }

        return {
          title,
          key: item.key,
        };
      });
    return (
      <div>
        <Search
          style={{ marginBottom: 8 }}
          placeholder="Search"
          onChange={this.onSearchChange}
        />
        <Tree
          onExpand={this.onTreeExpand}
          selectable={false}
          expandedKeys={expandedKeys}
          autoExpandParent={autoExpandParent}
          treeData={loop(this.gData)}
        />
      </div>
    );
  }
}

export default SearchTree;
