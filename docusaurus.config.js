const lightCodeTheme = require('prism-react-renderer/themes/github');
const darkCodeTheme = require('prism-react-renderer/themes/dracula');

/** @type {import('@docusaurus/types').DocusaurusConfig} */
module.exports = {
  title: 'YiriMirai',
  tagline: '一个轻量级、低耦合的基于 mirai-api-http 的 Python SDK。',
  url: 'https://yiri-mirai.vercel.app',
  baseUrl: '/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',
  organizationName: 'Wybxc',
  projectName: 'YiriMirai',
  themeConfig: {
    navbar: {
      title: 'YiriMirai',
      logo: {
        alt: 'Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'doc',
          docId: 'intro',
          position: 'left',
          label: '教程',
        },
        {
          href: 'https://yiri-mirai-api.vercel.app',
          label: 'API 文档',
          position: 'left'
        },
        {
          href: 'https://github.com/Wybxc/YiriMirai',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: '文档',
          items: [
            {
              label: '教程',
              to: '/docs/intro',
            },
            {
              href: 'https://yiri-mirai-api.vercel.app',
              label: 'API 文档',
            },
          ],
        },
        {
          title: '社区',
          items: [
            {
              label: 'Github Discussion',
              href: 'https://github.com/Wybxc/YiriMirai/discussions',
            },
            {
              label: 'Discord',
              href: 'https://discord.gg/RaXsHFC3PH',
            },
          ],
        },
        {
          title: '更多',
          items: [
            // {
            //   label: '博客',
            //   to: '/blog',
            // },
            {
              label: 'GitHub',
              href: 'https://github.com/Wybxc/YiriMirai',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} 忘忧北萱草，由 Docusaurus 2 构建。`,
    },
    prism: {
      theme: lightCodeTheme,
      darkTheme: darkCodeTheme,
    },
  },
  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          // Please change this to your repo.
          editUrl:
            'https://github.com/facebook/docusaurus/edit/master/website/',
        },
        blog: {
          showReadingTime: true,
          // Please change this to your repo.
          editUrl:
            'https://github.com/facebook/docusaurus/edit/master/website/blog/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
};
