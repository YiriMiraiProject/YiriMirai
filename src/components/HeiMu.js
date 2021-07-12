import React from "react";
import styles from "./HeiMu.module.css";

function HM(props) {
  return <div className={styles.HeiMu}>{props.children}</div>;
}

export default HM;
