async function removeHistory041(page) {
  if (page.id !== '126:51003' || page.name !== 'Knowledge Agent new') {
    throw Error('请切换到原文件的 Knowledge Agent new 页面后再运行。');
  }

  const title = 'Transformer и внимание';
  const layerName = 'Prototype click targets / locked for editing';
  const frames = page.children.filter(node => node.type === 'FRAME');
  const details = ['126:57007', '199:8803'].map(id => frames.find(frame => frame.id === id));
  if (details.every(detail => !detail)) {
    const remaining = frames.some(frame => frame.findAll(node =>
      (node.type === 'TEXT' && node.characters === '#041') ||
      (node.name === 'side-recent' && node.findAll(child => child.type === 'TEXT' && child.characters === title).length)
    ).length);
    if (remaining) throw Error('发现部分改动，请先在 Figma 撤销后重试。');
    return { alreadyRemoved: true };
  }

  const remove = new Set();
  const shift = [];
  const shrink = [];
  const counters = [];
  const reroute = [];
  const detailIds = new Set(details.filter(Boolean).map(node => node.id));
  let sidebars = 0;
  let historyRows = 0;

  function one(nodes, description) {
    if (nodes.length !== 1) throw Error(description + '：预期 1 个图层，实际 ' + nodes.length + ' 个。');
    return nodes[0];
  }
  const textNodes = node => node.findAll(child => child.type === 'TEXT');
  const layerOf = frame => one(frame.children.filter(node => node.name === layerName), frame.name + ' 的点击层');
  const actionList = reaction => reaction.actions || [reaction.action];
  function isBeingRemoved(node) {
    for (let ancestor = node; ancestor && ancestor !== page; ancestor = ancestor.parent) {
      if (remove.has(ancestor)) return true;
    }
    return false;
  }

  for (const [index, prefix] of ['', 'Dark · '].entries()) {
    const detail = details[index];
    const screens = frames.filter(frame => prefix ? frame.name.startsWith(prefix) &&
      /^\d+ · /.test(frame.name.slice(prefix.length)) : /^\d+ · /.test(frame.name));
    const screen = number => one(screens.filter(frame => frame.name.startsWith(prefix + number + ' · ')), prefix + number);
    const history = screen(38);
    const report = screen(15);
    if (screens.length !== 91 || detail !== screen(40) || detail.name !== prefix + '40 · ' + title ||
        !textNodes(detail).some(node => node.characters.startsWith('#041  '))) {
      throw Error('历史详情与当前文件不匹配。');
    }
    if ([history, report, detail].some(frame => frame.parent !== page) ||
        (page.flowStartingPoints || []).some(flow => detailIds.has(flow.nodeId))) {
      throw Error('原型的导航结构已变化。');
    }
    remove.add(detail);

    for (const frame of screens) {
      if (frame === detail) continue;
      const sidebar = one(frame.findAll(node => node.name === 'side-recent'), frame.name + ' 的最近记录');
      const second = one(sidebar.children.filter(node => 'findAll' in node &&
        textNodes(node).some(text => text.characters === title)), frame.name + ' 的第二条最近记录');
      if (sidebar.children[2] !== second) throw Error('最近记录顺序已变化：' + frame.name);
      remove.add(second);
      const layer = layerOf(frame);
      const recentHits = layer.children.filter(node => node.name === title);
      if (recentHits.length > 1 || (!recentHits.length && frame !== screen(13))) {
        throw Error('最近记录点击层与画面不匹配：' + frame.name);
      }
      recentHits.forEach(node => remove.add(node));
      sidebars++;
    }

    for (const number of [38, 58, 67, 72, 77]) {
      const frame = screen(number);
      const layer = layerOf(frame);
      const record = one(textNodes(frame).filter(text => text.characters === '#041'), frame.name + ' 的 #041');
      let row = record.parent;
      while (row && row !== frame && row.name !== 'tr') row = row.parent;
      if (!row || row === frame || !textNodes(row).some(text => text.characters === title)) {
        throw Error('历史列表中的 #041 行与预期不一致。');
      }
      const body = row.parent;
      const table = body.parent;
      const card = table.parent;
      if (body.name !== 'tbody' || table.name !== 'table' || card.name !== 'card history-card' ||
          [body, table, card].some(node => node.layoutMode !== 'NONE' || node.height <= row.height)) {
        throw Error('历史列表布局已变化：' + frame.name);
      }
      const rowHit = one(layer.children.filter(node => node.name.startsWith('#041' + title)), frame.name + ' 的 #041 点击层');
      if (!rowHit.reactions.some(reaction => actionList(reaction).some(action => action?.destinationId === detail.id))) {
        throw Error('历史记录的目标与详情不一致：' + frame.name);
      }
      remove.add(row);
      remove.add(rowHit);
      historyRows++;
      for (const nextRow of body.children.slice(body.children.indexOf(row) + 1)) {
        const recordId = one(textNodes(nextRow).filter(text => /^#\d+$/.test(text.characters)), nextRow.name + ' 的记录号').characters;
        const nextHit = one(layer.children.filter(node => node.name.startsWith(recordId)), recordId + ' 的点击层');
        shift.push([nextRow, nextRow.y - row.height], [nextHit, nextHit.y - row.height]);
      }
      for (const node of [body, table, card]) shrink.push([node, node.height - row.height]);

      for (const overview of frame.findAll(node => node.name === 'history-overview')) {
        for (const [label, before, after] of [['Обработки', '04', '03'], ['Завершено', '03', '02']]) {
          const metric = one(overview.children.filter(node => 'findAll' in node &&
            textNodes(node).some(text => text.characters === label)), label);
          const value = one(textNodes(metric).filter(text => text.characters === before), label + ' 的数量');
          counters.push([value, after]);
        }
      }
    }

    for (const frame of screens) {
      if (frame === detail) continue;
      for (const node of [frame, ...frame.findAll(node => 'reactions' in node && node.reactions.length)]) {
        if (isBeingRemoved(node)) continue;
        const needsUpdate = node.reactions.some(reaction =>
          actionList(reaction).some(action => action?.destinationId === detail.id));
        if (!needsUpdate) continue;
        let destination;
        if (frame === report && node.name === 'Открыть в истории') destination = history;
        if (/Граф знаний/.test(frame.name) && node.name === 'Открыть заметку') destination = report;
        if (!destination) throw Error('发现未识别的 #041 入口：' + frame.name + ' / ' + node.name);
        const reactions = node.reactions.map(reaction => ({
          trigger: reaction.trigger,
          actions: actionList(reaction).map(action => action?.destinationId === detail.id
            ? { ...action, destinationId: destination.id }
            : action)
        }));
        reroute.push([node, reactions]);
      }
    }
  }

  for (const [node] of counters) await figma.loadFontAsync(node.fontName);
  for (const [node, reactions] of reroute) await node.setReactionsAsync(reactions);
  for (const [node, y] of shift) node.y = y;
  for (const [node, height] of shrink) node.resizeWithoutConstraints(node.width, height);
  for (const [node, value] of counters) node.characters = value;
  for (const node of remove) node.remove();

  const remaining = page.children.filter(node => node.type === 'FRAME');
  if (remaining.some(frame => detailIds.has(frame.id))) throw Error('历史详情删除未完成。');
  for (const frame of remaining.filter(node => /^(?:Dark · )?\d+ · /.test(node.name))) {
    if (frame.findAll(node => (node.type === 'TEXT' && node.characters === '#041') ||
      (node.name === 'side-recent' && textNodes(node).some(text => text.characters === title))).length) {
      throw Error('还有 #041 内容留在 ' + frame.name);
    }
    if ([frame, ...frame.findAll(node => 'reactions' in node && node.reactions.length)].some(node =>
      node.reactions.some(reaction => actionList(reaction).some(action => detailIds.has(action?.destinationId))))) {
      throw Error('还有原型连线指向已删除的画面：' + frame.name);
    }
  }
  return { sidebars, historyRows, detailScreens: details.length, rerouted: reroute.length };
}

if (typeof figma !== 'undefined') {
  figma.showUI(__html__, { width: 380, height: 208, themeColors: true });
  figma.ui.onmessage = async message => {
    if (message.type !== 'remove041') return;
    try {
      figma.ui.postMessage({ type: 'done', result: await removeHistory041(figma.currentPage) });
    } catch (error) {
      figma.ui.postMessage({ type: 'error', message: String(error.message || error) });
    }
  };
}
