const lightCodeTheme = require("prism-react-renderer/themes/github");
const darkCodeTheme = require("prism-react-renderer/themes/dracula");

/** @type {import('@docusaurus/types').DocusaurusConfig} */
module.exports = {
  title: "YiriMirai",
  tagline: "一个轻量级、低耦合的基于 mirai-api-http 的 Python SDK。",
  url: "https://yiri-mirai.vercel.app",
  baseUrl: "/",
  onBrokenLinks: "throw",
  onBrokenMarkdownLinks: "warn",
  favicon: "img/favicon.ico",
  organizationName: "YiriMiraiProject",
  projectName: "YiriMirai",
  i18n: {
    defaultLocale: "zh-CN",
    locales: ["zh-CN"],
    localeConfigs: {
      "zh-CN": {
        label: "简体中文",
        direction: "ltr",
      },
    },
  },
  themeConfig: {
    navbar: {
      title: "YiriMirai",
      logo: {
        alt: "Logo",
        src: "img/logo.svg",
      },
      items: [
        {
          label: "文档",
          position: "left",
          type: "doc",
          docId: "intro",
        },
        {
          label: "教程",
          position: "left",
          type: "doc",
          docId: "intro",
          docsPluginId: "tutorials"
        },
        {
          to: "/blog",
          label: "博客",
          position: "left",
        },
        {
          href: "https://yiri-mirai-api.vercel.app",
          label: "API 文档",
          position: "left",
        },
        {
          href: "https://github.com/YiriMiraiProject/YiriMirai",
          label: "GitHub",
          position: "right",
        },
      ],
    },
    footer: {
      style: "dark",
      links: [
        {
          title: "文档",
          items: [
            {
              label: "教程",
              to: "/docs/intro",
            },
            {
              href: "https://yiri-mirai-api.vercel.app",
              label: "API 文档",
            },
          ],
        },
        {
          title: "社区",
          items: [
            {
              label: "QQ 群：766952599",
              href: "https://jq.qq.com/?_wv=1027&k=PXBOuBCI",
            },
            {
              label: "Github Discussion",
              href: "https://github.com/YiriMiraiProject/YiriMirai/discussions",
            },
            {
              label: "Discord",
              href: "https://discord.gg/RaXsHFC3PH",
            },
          ],
        },
        {
          title: "更多",
          items: [
            {
              label: "博客",
              to: "/blog",
            },
            {
              label: "GitHub",
              href: "https://github.com/YiriMiraiProject/YiriMirai",
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} YiriMiraiProject，由 Docusaurus 2 构建。`,
    },
    prism: {
      theme: lightCodeTheme,
      darkTheme: darkCodeTheme,
    },
  },
  presets: [
    [
      "@docusaurus/preset-classic",
      {
        docs: {
          sidebarPath: require.resolve("./sidebars.js"),
          editUrl: "https://github.com/YiriMiraiProject/YiriMirai/edit/doc/",
        },
        blog: {
          blogTitle: "博客",
          blogDescription: "YiriMirai 的开发笔记，以及其他。",
          blogSidebarCount: 5,
          blogSidebarTitle: "最近的博文",
          showReadingTime: false,
          editUrl: "https://github.com/YiriMiraiProject/YiriMirai/edit/blog/",
        },
        theme: {
          customCss: [require.resolve("./src/css/custom.css")],
        },
        gtag: {
          trackingID: 'G-L0N9H6KGGW',
          anonymizeIP: true, // Should IPs be anonymized?
        },
      },
    ],
  ],
  plugins: [
    [
      require.resolve("@easyops-cn/docusaurus-search-local"),
      {
        // `hashed` is recommended as long-term-cache of index file is possible.
        hashed: true,
        language: ["en", "zh"],
        translations: {
          search_placeholder: "搜索",
          see_all_results: "查看所有结果……",
          no_results: "无结果。",
          search_results_for: "“{{ keyword }}”的搜索结果",
          search_the_documentation: "搜索文档",
          count_documents_found: "找到{{ count }}篇文档。",
          no_documents_were_found: "没有找到包含指定关键词的文档。",
        },
        highlightSearchTermsOnTargetPage: true,
      },
    ],
    [
      "@docusaurus/plugin-content-docs",
      {
        id: "tutorials",
        path: "tutorials",
        routeBasePath: "tutorials",
        editUrl: "https://github.com/YiriMiraiProject/YiriMirai/edit/tutorials/",
      },
    ],
  ],
};
