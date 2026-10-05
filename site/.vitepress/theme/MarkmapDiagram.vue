<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from 'vue';
import { useData } from 'vitepress';
const props = defineProps({ data: { type: String, required: true }, source: { type: String, required: true } });
const { isDark } = useData();
const svg = ref(null);
const source = ref('');
const ready = ref(false);
const error = ref('');
let map, tree, observer, alive = true;
const decode = value => new TextDecoder().decode(Uint8Array.from(atob(value), char => char.charCodeAt(0)));
const colors = () => isDark.value ? ['#80d2c2', '#b1bef1', '#f1c88a', '#9dccfa', '#e8aad1'] : ['#207c70', '#5869b2', '#a87125', '#357ca7', '#a65f87'];
async function fit() { if (map) await map.fit(); }
async function expand(level) { if (map) { await map.setData(structuredClone(tree), { initialExpandLevel: level }); await fit(); } }
onMounted(async () => {
  try {
    source.value = decode(props.source);
    tree = JSON.parse(decode(props.data));
    const { Markmap } = await import('markmap-view');
    if (!alive || !svg.value) return;
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    map = Markmap.create(svg.value, { initialExpandLevel: 2, maxWidth: 260, duration: reduceMotion ? 0 : 180, color: node => colors()[Math.max(0, (node.state?.id || 1) - 1) % 5] }, structuredClone(tree));
    await fit();
    if (!alive) return;
    observer = new ResizeObserver(() => { fit(); });
    observer.observe(svg.value);
    ready.value = true;
  } catch {
    error.value = '脑图暂时无法显示，可直接使用下方大纲与资料链接。';
  }
});
watch(isDark, () => { if (map) { map.setOptions({ color: node => colors()[Math.max(0, (node.state?.id || 1) - 1) % 5] }); map.renderData(); } });
onBeforeUnmount(() => { alive = false; observer?.disconnect(); map?.destroy(); });
</script>

<template>
  <figure class="study-mindmap">
    <figcaption><strong>课程与复习脑图</strong><span>点击节点展开，拖动与滚轮缩放</span></figcaption>
    <div class="mindmap-toolbar" role="group" aria-label="脑图视图">
      <button type="button" :disabled="!ready" @click="expand(-1)">展开全部</button>
      <button type="button" :disabled="!ready" @click="expand(1)">收起层级</button>
      <button type="button" :disabled="!ready" @click="fit">适应画布</button>
    </div>
    <svg ref="svg" class="markmap-svg" aria-label="可展开的课程复习脑图" role="img"></svg>
    <p v-if="error" role="status">{{ error }}</p>
    <details><summary>查看脑图大纲</summary><pre>{{ source }}</pre></details>
  </figure>
</template>
