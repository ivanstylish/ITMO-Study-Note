import { defineConfig } from 'vitepress';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { safeMarkdown } from './safe-markdown.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const catalog = JSON.parse(fs.readFileSync(path.join(root, 'navigation/catalog.json'), 'utf8'));
const manifest = JSON.parse(fs.readFileSync(path.join(root, '.build/site-manifest.json'), 'utf8'));
const route = file => '/' + (file === 'README.md' ? '' : file.replace(/(?:^|\/)index\.md$/i, '/').replace(/\.md$/i, ''));
const semesters = catalog.semesters.map(semester => ({
  text: `第 ${semester.number} 学期`,
  link: `/academic/semester-${String(semester.number).padStart(2, '0')}`,
  collapsed: true,
  items: catalog.courses.filter(course => course.semesters.includes(semester.number))
    .map(course => ({ text: course.title, link: route(course.dashboard) }))
}));

export default defineConfig({
  srcDir: '../.build/docs',
  outDir: '../.build/site',
  cacheDir: '../.build/cache',
  base: process.env.DOCS_BASE || '/',
  title: 'ITMO · Study Notes',
  description: '大学知识库、考试复习与实验答辩 / Конспекты, повторение и защита лабораторных',
  lang: 'zh-CN',
  appearance: true,
  cleanUrls: false,
  // These are addresses at which students run labs, not routes of this site.
  ignoreDeadLinks: [/^https?:\/\/(?:localhost|127\.0\.0\.1)(?::\d+)?(?:\/|$)/],
  markdown: {
    html: false,
    attrs: { disable: true },
    math: true,
    languageAlias: { assembly: 'asm', jsp: 'java', shell: 'sh' },
    lineNumbers: false,
    config(md) { safeMarkdown(md, manifest, { base: process.env.DOCS_BASE || '/' }); }
  },
  themeConfig: {
    siteTitle: 'ITMO 学习笔记',
    nav: [
      { text: '学期与课程', link: '/navigation/courses' },
      { text: '知识索引', link: '/knowledge/' },
      { text: '复习脑图', link: '/knowledge/mindmap' },
      { text: '复习', link: '/study/revision' },
      { text: '答辩', link: '/study/defense' }
    ],
    sidebar: [
      { text: '学习入口', items: [
        { text: '首页', link: '/' },
        { text: '课程总览', link: '/navigation/courses' },
        { text: '知识关联', link: '/knowledge/' },
        { text: '复习脑图', link: '/knowledge/mindmap' },
        { text: '资料反向关联', link: '/knowledge/backlinks' },
        { text: '考试复习', link: '/study/revision' },
        { text: '实验答辩', link: '/study/defense' }
      ] },
      ...semesters,
      { text: '使用与维护', collapsed: true, items: [
        { text: '导航说明', link: '/navigation/' },
        { text: '网站说明', link: '/navigation/website' }
      ] }
    ],
    outline: { level: [2, 3], label: '本页目录' },
    docFooter: { prev: '上一页', next: '下一页' },
    darkModeSwitchLabel: '切换深浅色',
    sidebarMenuLabel: '课程导航',
    returnToTopLabel: '返回顶部',
    search: {
      provider: 'local',
      options: {
        detailedView: true,
        miniSearch: {
          options: {
            // Latin/Cyrillic words + individual Han characters keep Chinese and
            // Russian notes searchable without a remote search service.
            tokenize: text => text.toLowerCase().replace(/\p{Script=Han}/gu, char => ` ${char} `).match(/[\p{L}\p{N}_]+/gu) || []
          },
          searchOptions: { prefix: true, fuzzy: 0.2, combineWith: 'AND' }
        },
        translations: {
          button: { buttonText: '搜索笔记', buttonAriaLabel: '搜索中俄双语笔记' },
          modal: { noResultsText: '没有找到结果', resetButtonTitle: '清空搜索',
            footer: { selectText: '选择', navigateText: '切换', closeText: '关闭' } }
        }
      }
    },
    socialLinks: [{ icon: 'github', link: manifest.repository }],
    footer: { message: '原始 Markdown 是唯一内容来源；代码与报告在 GitHub 仓库中。' }
  },
  vite: { build: { chunkSizeWarningLimit: 1300 } }
});
