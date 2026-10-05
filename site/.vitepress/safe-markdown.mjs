import path from 'node:path';
import { Transformer } from 'markmap-lib/no-plugins';

const encodePath = value => value.split('/').map(encodeURIComponent).join('/');

export function safeMarkdown(md, manifest, { base = '/' } = {}) {
  const transformer = new Transformer();
  transformer.md.set({ html: false });
  // General attribute syntax mistakes mathematical sets for HTML attributes.
  // Only explicit heading anchors from our navigation projection are supported.
  md.core.ruler.before('anchor', 'repository-heading-anchors', state => {
    for (let index = 0; index < state.tokens.length - 1; index++) {
      const heading = state.tokens[index];
      const inline = state.tokens[index + 1];
      if (heading.type !== 'heading_open' || inline.type !== 'inline') continue;
      const match = inline.content.match(/\s+\{#([A-Za-z][\w:-]*)\}$/);
      if (!match) continue;
      heading.attrSet('id', match[1]);
      inline.content = inline.content.slice(0, -match[0].length);
      const last = inline.children?.at(-1);
      if (last?.type === 'text') last.content = last.content.replace(/\s+\{#[A-Za-z][\w:-]*\}$/, '');
    }
  });
  const files = new Map(manifest.files.map(file => [file.toLowerCase(), file]));
  const pages = new Set(manifest.pages);
  const directories = new Map(manifest.directories.map(directory => [directory.toLowerCase(), directory]));
  const github = (file, image = false) => image
    ? `https://raw.githubusercontent.com/ivanstylish/ITMO-Study-Note/${encodeURIComponent(manifest.branch)}/${encodePath(file)}`
    : `${manifest.repository}/blob/${encodeURIComponent(manifest.branch)}/${encodePath(file)}`;
  function resolve(href, env, image = false) {
    if (!href || /^(?:https?:|mailto:|#|data:)/i.test(href)) return href;
    if (/^(?:javascript:|file:|[a-z]:[\\/])/i.test(href)) return null;
    const hashAt = href.indexOf('#');
    const anchor = hashAt < 0 ? '' : href.slice(hashAt);
    let clean = hashAt < 0 ? href : href.slice(0, hashAt);
    try { clean = decodeURIComponent(clean); } catch { /* preserve malformed legacy URL */ }
    clean = clean.replaceAll('\\', '/');
    const current = (env.relativePath || '').replaceAll('\\', '/');
    const original = current === 'index.md' ? 'README.md' : current;
    const candidate = path.posix.normalize(clean.startsWith('/') ? clean.slice(1) : path.posix.join(path.posix.dirname(original), clean));
    const directory = directories.get(candidate.replace(/\/$/, '').toLowerCase());
    if (directory && !image) return `${manifest.repository}/tree/${encodeURIComponent(manifest.branch)}/${encodePath(directory)}` + anchor;
    let target = files.get(candidate.toLowerCase());
    if (!target) {
      for (const suffix of ['/index.md', '/readme.md', '.md']) {
        target = files.get((candidate.replace(/\/$/, '') + suffix).toLowerCase());
        if (target) break;
      }
    }
    if (!target) return null;
    if (image) return github(target, true);
    if (!pages.has(target)) return github(target) + anchor;
    return '/' + (target === 'README.md' ? 'index.md' : target) + anchor;
  }
  md.core.ruler.push('repository-safe-links', state => {
    for (const token of state.tokens) {
      for (const child of token.children || []) {
        if (child.type === 'link_open') {
          const href = resolve(child.attrGet('href'), state.env);
          if (href) child.attrSet('href', href);
          else {
            child.attrSet('href', '#');
            child.attrSet('title', '原笔记链接缺失或仅在作者本地可用');
            child.attrSet('class', 'legacy-missing-link');
          }
        } else if (child.type === 'image') {
          const src = resolve(child.attrGet('src'), state.env, true);
          if (src) child.attrSet('src', src);
          else {
            child.type = 'text';
            child.content = `[原图未收录：${child.content || '图片'}]`;
          }
        }
      }
    }
  });
  // Vue expressions in old notes are examples, never executable templates.
  const textRenderer = md.renderer.rules.text;
  md.renderer.rules.text = (tokens, index, options, env, self) => {
    const rendered = textRenderer ? textRenderer(tokens, index, options, env, self) : md.utils.escapeHtml(tokens[index].content);
    return rendered.replaceAll('{{', '&#123;&#123;').replaceAll('}}', '&#125;&#125;')
      .replace(/✓ 已通过|○ 待通过|— 未标记/g, label => `<span class="study-status ${label.startsWith('✓') ? 'passed' : label.startsWith('○') ? 'pending' : 'unmarked'}">${label}</span>`);
  };
  const fence = md.renderer.rules.fence;
  md.renderer.rules.fence = (tokens, index, options, env, self) => {
    if (tokens[index].info.trim() === 'course-cards' && env.relativePath === 'navigation/courses.md') return '<CourseExplorer />';
    if (tokens[index].info.trim() === 'markmap') {
      const content = tokens[index].content;
      const linked = content.replace(/(\[[^\]\n]*\]\()((?:[^()\s]|\([^()\s]*\))*)\)/g, (_, label, href) => {
        let target = resolve(href, env) || '#';
        if (target.startsWith('/')) target = base.replace(/\/$/, '') + target.replace(/\.md(?=#|$)/, '.html');
        return `${label}${target})`;
      });
      const data = Buffer.from(JSON.stringify(transformer.transform(linked).root), 'utf8').toString('base64');
      const source = Buffer.from(content, 'utf8').toString('base64');
      return `<MarkmapDiagram data="${data}" source="${source}" />`;
    }
    if (tokens[index].info.trim() === 'mermaid') {
      const source = Buffer.from(tokens[index].content, 'utf8').toString('base64');
      return `<MermaidDiagram source="${source}" />`;
    }
    return fence(tokens, index, options, env, self);
  };
}
