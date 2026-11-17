figma.showUI(__html__, { width: 400, height: 580, themeColors: true });
const editable = n => n.type === 'FRAME' || n.type === 'COMPONENT';
const isButton = n => /^btn(?:\s|$)/.test(n.name);
const allNodes = root => [root, ...root.findAll(() => true)];

async function loadFonts(root) {
  const fonts = new Map();
  for (const n of allNodes(root)) {
    if (n.type !== 'TEXT' || !n.characters.length) continue;
    for (const s of n.getStyledTextSegments(['fontName'])) fonts.set(JSON.stringify(s.fontName), s.fontName);
  }
  for (const font of fonts.values()) await figma.loadFontAsync(font);
}

function borderCandidate(n) {
  if (!editable(n)) return null;
  const sides = n.children.filter(c => /^Border \/ (top|right|bottom|left)$/.test(c.name));
  if (sides.length !== 4 || new Set(sides.map(s => s.name)).size !== 4) return null;
  const bySide = Object.fromEntries(sides.map(s => [s.name.split(' / ')[1], s]));
  if (sides.some(s => s.type !== 'RECTANGLE' || !s.visible || s.opacity !== 1 || s.effects.length || s.strokes.length || !Array.isArray(s.fills) || s.fills.length !== 1 || s.fills[0].type !== 'SOLID')) return null;
  const weight = bySide.top.height, near = (a, b) => Math.abs(a - b) < 0.1;
  if (!(weight > 0 && weight <= 4) || !near(bySide.bottom.height, weight) || !near(bySide.left.width, weight) || !near(bySide.right.width, weight)) return null;
  const expected = { top: [0, 0, n.width, weight], bottom: [0, n.height - weight, n.width, weight], left: [0, 0, weight, n.height], right: [n.width - weight, 0, weight, n.height] };
  for (const [side, values] of Object.entries(expected)) if (!['x', 'y', 'width', 'height'].every((key, i) => near(bySide[side][key], values[i]))) return null;
  const paint = JSON.stringify(sides[0].fills);
  if (sides.some(s => JSON.stringify(s.fills) !== paint || s.reactions.length)) return null;
  return { sides, weight, fills: JSON.parse(paint) };
}

function repairBorder(n) {
  const candidate = borderCandidate(n);
  if (!candidate) return false;
  n.strokes = candidate.fills; n.strokeWeight = candidate.weight; n.strokeAlign = 'INSIDE';
  for (const side of candidate.sides) side.remove();
  return true;
}

function horizontal(n) {
  n.layoutMode = 'HORIZONTAL'; n.primaryAxisSizingMode = n.counterAxisSizingMode = 'FIXED';
  n.primaryAxisAlignItems = 'MIN'; n.counterAxisAlignItems = 'CENTER';
}

function rightAlignCell(cell, width) {
  cell.resize(width, cell.height); cell.layoutSizingHorizontal = 'FIXED';
  for (const t of cell.findAll(n => n.type === 'TEXT')) {
    t.textAutoResize = 'HEIGHT'; t.resize(width, t.height); t.x = 0; t.textAlignHorizontal = 'RIGHT';
  }
}

function repairFileCard(card) {
  const rows = card.children.filter(n => n.name === 'file-option' && editable(n));
  const header = card.children.find(n => n.name === 'card-head' && editable(n));
  if (!rows.length || !header) return 0;
  // Only the known three-cell file picker can be converted without guessing.
  const cells = row => row.children.filter(n => !/^Border \/ /.test(n.name));
  if (rows.some(r => { const c = cells(r); return r.width < 500 || c.length !== 3 || !editable(c[0]) || !editable(c[1]) || !isButton(c[2]); })) return 0;
  const sizeHeader = header.children.find(n => editable(n) && n.findAll(c => c.type === 'TEXT' && c.characters === 'Размер').length);
  if (!sizeHeader) return 0;
  for (const row of rows) {
    const [name, size, button] = cells(row);
    horizontal(row); row.paddingLeft = row.paddingRight = row.paddingTop = row.paddingBottom = 20; row.itemSpacing = 24;
    for (const child of row.children) if (/^Border \/ /.test(child.name)) child.layoutPositioning = 'ABSOLUTE';
    button.resize(88, button.height); button.layoutSizingHorizontal = 'FIXED'; rightAlignCell(size, 80);
    horizontal(name); name.paddingLeft = name.paddingRight = name.paddingTop = name.paddingBottom = 0; name.itemSpacing = 10;
    name.resize(row.width - 256, Math.max(24, name.height)); name.layoutSizingHorizontal = 'FILL';
    const label = name.children.find(n => n.type === 'TEXT');
    if (label) { label.textAutoResize = 'HEIGHT'; label.resize(name.width - 29, label.height); label.layoutSizingHorizontal = 'FILL'; }
  }
  horizontal(header); header.paddingLeft = header.paddingRight = 20; header.paddingTop = header.paddingBottom = 0; header.itemSpacing = 24;
  const title = header.children.find(n => n !== sizeHeader && n.name !== 'Action column spacer');
  if (title) { title.resize(header.width - 256, title.height); title.layoutSizingHorizontal = 'FILL'; }
  rightAlignCell(sizeHeader, 80);
  let spacer = header.children.find(n => n.name === 'Action column spacer');
  if (!spacer) { spacer = figma.createFrame(); spacer.name = 'Action column spacer'; spacer.fills = []; header.appendChild(spacer); }
  spacer.resize(88, 1); spacer.layoutSizingHorizontal = 'FIXED';
  return rows.length;
}

function audit(page) {
  const nodes = page.findAll(() => true);
  return { editableButtons: nodes.filter(n => editable(n) && isButton(n)).length,
    borderCandidates: nodes.filter(n => borderCandidate(n)).length,
    fileRows: nodes.filter(n => n.name === 'file-option' && editable(n)).length,
    prototypeTargets: nodes.reduce((sum, n) => sum + ('reactions' in n ? n.reactions.length : 0), 0) };
}

async function repair(page) {
  await loadFonts(page);
  // Descendants of an instance inherit corrections from its main component.
  const nodes = page.findAll(() => true).filter(n => { let p = n.parent; while (p && p !== page) { if (p.type === 'INSTANCE') return false; p = p.parent; } return true; });
  let borders = 0, rows = 0; const mutatedNodeIds = [];
  for (const n of nodes) if (repairBorder(n)) { borders++; mutatedNodeIds.push(n.id); }
  for (const n of nodes) if (editable(n) && n.children.some(c => c.name === 'file-option')) {
    const count = repairFileCard(n); if (count) { rows += count; mutatedNodeIds.push(...allNodes(n).map(c => c.id)); }
  }
  return { borders, rows, mutatedNodeIds: [...new Set(mutatedNodeIds)], after: audit(page) };
}

const themes = [
  { name: 'A · Тихий сад', colors: ['#f7f8f6','#ffffff','#232621','#d1fca6','#34745c'] },
  { name: 'B · Бумажный архив', colors: ['#f6f3eb','#fffdf8','#283b32','#dce7bf','#4b6b51'] },
  { name: 'C · Атлас идей', colors: ['#f4f5fa','#ffffff','#303343','#e1dcf7','#34745c'] }
];
const rgb = hex => ({ r: parseInt(hex.slice(1,3),16)/255, g: parseInt(hex.slice(3,5),16)/255, b: parseInt(hex.slice(5,7),16)/255 });
const paint = hex => [{ type:'SOLID', color:rgb(hex) }];
const sameColor = (a,b) => ['r','g','b'].every(k => Math.abs(a[k]-b[k]) < 0.002);

async function makeComparisons(sourcePage) {
  const selected = sourcePage.selection[0];
  const source = selected && selected.type === 'FRAME' && selected.parent === sourcePage ? selected : sourcePage.children.find(n => n.type === 'FRAME' && /^01\s*[·.]/.test(n.name));
  if (!source) throw new Error('请先选中一个完整的原型画面（顶层 Frame），再生成比较稿。');
  await loadFonts(source); const font = { family:'Inter', style:'Regular' }; await figma.loadFontAsync(font);
  const page = figma.createPage(); page.name = 'Stage 4 · 可编辑个性化比较'; await figma.setCurrentPageAsync(page);
  const frames = [], tabs = [], createdNodeIds = [page.id];
  for (let index = 0; index < themes.length; index++) {
    const theme = themes[index], colors = theme.colors;
    const wrapper = figma.createFrame(); page.appendChild(wrapper); wrapper.name = theme.name;
    wrapper.resize(source.width, source.height + 72); wrapper.x = index*(source.width+120); wrapper.y = 0; wrapper.fills = paint(colors[0]);
    const screen = source.clone(); wrapper.appendChild(screen); screen.x = 0; screen.y = 72;
    for (const n of allNodes(screen)) for (const prop of ['fills','strokes']) {
      if (!(prop in n) || !Array.isArray(n[prop])) continue;
      const next = n[prop].map(p => {
        if (p.type !== 'SOLID') return p;
        const i = themes[0].colors.findIndex(c => sameColor(p.color,rgb(c)));
        return i < 0 ? p : { ...p, color:rgb(colors[i]), boundVariables:{} };
      });
      if (JSON.stringify(n[prop]) !== JSON.stringify(next)) n[prop] = next;
    }
    const toolbar = figma.createFrame(); wrapper.appendChild(toolbar); toolbar.name = 'Theme comparison tabs'; toolbar.resize(source.width,72); toolbar.fills=paint(colors[1]);
    horizontal(toolbar); toolbar.paddingLeft=toolbar.paddingRight=24; toolbar.itemSpacing=12;
    const buttons=[];
    for (let i=0;i<themes.length;i++) {
      const b=figma.createFrame();toolbar.appendChild(b);b.name=themes[i].name;b.layoutMode='HORIZONTAL';
      b.paddingLeft=b.paddingRight=16;b.paddingTop=b.paddingBottom=10;b.primaryAxisSizingMode=b.counterAxisSizingMode='AUTO';b.cornerRadius=11;b.fills=paint(i===index?colors[2]:colors[0]);
      const t=figma.createText();b.appendChild(t);t.fontName=font;t.fontSize=12;t.characters=themes[i].name;t.fills=paint(i===index?colors[1]:colors[2]);buttons.push(b);
    }
    frames.push(wrapper);tabs.push(buttons);createdNodeIds.push(...allNodes(wrapper).map(n=>n.id));
  }
  for (const buttons of tabs) for (let i=0;i<buttons.length;i++) await buttons[i].setReactionsAsync([{trigger:{type:'ON_CLICK'},actions:[{type:'NODE',destinationId:frames[i].id,navigation:'NAVIGATE',transition:null,preserveScrollPosition:false}]}]);
  page.flowStartingPoints=[{nodeId:frames[0].id,name:'A / B / C · 个性化比较'}];page.selection=[frames[0]];figma.viewport.scrollAndZoomIntoView([frames[0]]);
  return {createdNodeIds,screens:frames.map(n=>({id:n.id,name:n.name})),note:'三个方案仅比较配色；已有流程仍跳转到原型原有画面。'};
}

figma.ui.onmessage=async message=>{
  try {
    const page=figma.currentPage;
    if(message.type==='audit')figma.ui.postMessage({type:'result',result:audit(page)});
    if(message.type==='repair')figma.ui.postMessage({type:'result',result:await repair(page)});
    if(message.type==='compare')figma.ui.postMessage({type:'result',result:await makeComparisons(page)});
  } catch(error) {figma.ui.postMessage({type:'error',message:String(error.message||error)});}
};
