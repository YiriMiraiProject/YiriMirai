import React from "react";
import { List, Avatar, Divider, Card } from "antd";
import { UserOutlined } from "@ant-design/icons";
import styles from "./ChatMessage.module.css";

const avatarMap = {
  忘忧北萱草: require("@site/static/img/avatars/忘忧北萱草.jpg").default,
  Yiri: require("@site/static/img/avatars/Yiri.jpg").default,
};

class ChatBox extends React.Component {
  render() {
    return (
      <div className={styles.panelView}>
        <div className={styles.controls}>
          <div className={styles.circleRed} />
          <div className={styles.circleYellow} />
          <div className={styles.circleGreen} />
          <div className={styles.title}>聊天记录</div>
        </div>
        <div className={styles.content}>{this.props.children}</div>
      </div>
    );
  }
}

class ChatMessage extends React.Component {
  constructor(props) {
    super(props);

    this.name = props.name;
    this.msg = props.msg || props.message;

    let avatar;
    if (!props.avatar) {
      if (avatarMap[props.name]) {
        avatar = <Avatar src={avatarMap[props.name]} className={styles.avatar} />;
      } else {
        avatar = <Avatar icon={<UserOutlined />} className={styles.avatar} />;
      }
    } else {
      avatar = <Avatar src={item.avatar} className={styles.avatar}/>;
    }
    this.avatar = avatar;
  }

  render() {
    return (
      <div className={styles.chatMessage}>
        {this.avatar}
        <div className={styles.nickname}>{this.name}</div>
        <div className={styles.messageBox}>{this.msg}</div>
      </div>
    );
  }
}

export { ChatBox, ChatMessage };
