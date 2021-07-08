import React from "react";
import { AiOutlineUser } from "react-icons/ai";
import styles from "./ChatMessage.module.css";
import Observer from "@researchgate/react-intersection-observer";

const avatarMap = {
  忘忧北萱草: require("@site/static/img/avatars/忘忧北萱草.jpg").default,
  Yiri: require("@site/static/img/avatars/Yiri.jpg").default,
};

function Avatar(props) {
  let img;
  if (props.src) {
    img = <img src={props.src} alt={props.name} />;
  } else {
    if (props.name in avatarMap) {
      img = <img src={avatarMap[props.name]} alt={props.name} />;
    } else {
      img = <AiOutlineUser alt={props.name} />;
    }
  }
  return (
    <div
      {...props}
      className={"avatar__photo" + " " + props.className || ""}
      style={{
        backgroundColor: "var(--ifm-color-gray-400)",
      }}
    >
      {img}
    </div>
  );
}

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

    this.state = { shown: false };

    this.name = props.name;
    this.msg = props.msg || props.message;

    this.avatar = <Avatar name={this.props.name} className={styles.avatar} />;
  }

  onChange = (event, unobserve) => {
    if (event.isIntersecting) {
      unobserve();
      this.setState({ shown: true });
    }
  };

  render() {
    return (
      <Observer onChange={this.onChange}>
        <div
          className={
            this.state.shown ? styles.chatMessageShown : styles.chatMessage
          }
        >
          {this.avatar}
          <div className={styles.nickname}>{this.name}</div>
          <div className={styles.messageBox}>{this.msg}</div>
        </div>
      </Observer>
    );
  }
}

export { ChatBox, ChatMessage };
