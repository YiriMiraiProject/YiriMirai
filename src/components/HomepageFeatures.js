import React from 'react';
import clsx from 'clsx';
import styles from './HomepageFeatures.module.css';

const FeatureList = [
  {
    title: '轻量',
    Svg: require('../../static/img/YiriMirai_Lite.svg').default,
    description: (
      <>
        YiriMirai 的定位是 SDK 而非框架，它更接近底层。我们尽可能地把一切变得简单，纯粹地和 Mirai 通信。
        YiriMirai 不提供模块化，因为这不是每个人的需要。
      </>
    ),
  },
  {
    title: '易于使用',
    Svg: require('../../static/img/YiriMirai_Easy.svg').default,
    description: (
      <>
        YiriMirai 支持以足够简洁明了的方式来编写您的代码。正如我们说过的，要把一切变得简单。
      </>
    ),
  },
  {
    title: '如果想要更多……',
    Svg: require('../../static/img/YiriMirai_More.svg').default,
    description: (
      <>
        如果你更喜欢模块化的方式，不妨去试一试 <a href="https://github.com/GraiaProject/Application">Graia Framework</a>。
        这是一个更加强大的框架，提供了 Saya 这一模块化方式。
      </>
    ),
  },
];

function Feature({ Svg, title, description }) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} alt={title} />
      </div>
      <div className="padding-horiz--md">
        <h3 className="text--center">{title}</h3>
        <p className="text--left">{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
