<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import { useData } from 'vitepress';

const props = defineProps({ source: { type: String, required: true } });
const container = ref(null);
const error = ref('');
const { isDark } = useData();
const sourceText = computed(() => {
  if (typeof atob === 'undefined') return '';
  return new TextDecoder().decode(Uint8Array.from(atob(props.source), char => char.charCodeAt(0)));
});
let version = 0;
async function draw() {
  const current = ++version;
  if (!container.value) return;
  try {
    const { default: mermaid } = await import('mermaid');
    mermaid.initialize({ startOnLoad: false, securityLevel: 'strict', theme: isDark.value ? 'dark' : 'default', suppressErrorRendering: true });
    const id = `study-mermaid-${crypto.randomUUID().replaceAll('-', '')}`;
    const result = await mermaid.render(id, sourceText.value);
    if (current !== version || !container.value) return;
    container.value.innerHTML = result.svg;
    error.value = '';
  } catch {
    error.value = '图表暂时无法渲染，可展开查看 Mermaid 原文。';
  }
}
onMounted(draw);
watch(isDark, draw);
watch(() => props.source, draw);
</script>

<template>
  <figure class="knowledge-diagram">
    <div ref="container" aria-label="知识关联图" role="img"></div>
    <p v-if="error" role="status">{{ error }}</p>
    <details><summary>查看图表原文</summary><pre>{{ sourceText }}</pre></details>
  </figure>
</template>
