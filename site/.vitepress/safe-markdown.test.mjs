import test from 'node:test';
import assert from 'node:assert/strict';
import MarkdownIt from 'markdown-it';
import { safeMarkdown } from './safe-markdown.mjs';

test('inline template examples remain literal in the reading site', () => {
  const md = new MarkdownIt();
  md.core.ruler.push('anchor', () => {});
  safeMarkdown(md, { files: [], pages: [], directories: [] });
  const html = md.render('tooltip 中的 `{{ ... }}` 原样保留。');
  assert.match(html, /<code>&#123;&#123; \.\.\. &#125;&#125;<\/code>/);
  assert.ok(!html.includes('{{'));
});
