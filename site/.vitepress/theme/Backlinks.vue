<script setup>
import { computed } from 'vue';
import { useData, withBase } from 'vitepress';
import backlinks from '../../../.build/backlinks.json';
const { page } = useData();
const incoming = computed(() => backlinks[page.value.relativePath === 'index.md' ? 'README.md' : page.value.relativePath] || []);
const route = file => withBase('/' + (file === 'README.md' ? 'index' : file.slice(0, -3)).split('/').map(encodeURIComponent).join('/') + '.html');
</script>

<template>
  <section v-if="incoming.length && page.relativePath !== 'index.md'" class="study-backlinks" aria-label="资料反向关联">
    <div class="study-backlinks-heading"><h2>哪些页面引用了这里</h2><span>{{ incoming.length }} 个入口</span></div>
    <ul><li v-for="source in incoming.slice(0, 8)" :key="source.path"><a :href="route(source.path)">{{ source.title }}</a></li></ul>
    <details v-if="incoming.length > 8"><summary>展开其余 {{ incoming.length - 8 }} 个入口</summary>
      <ul><li v-for="source in incoming.slice(8)" :key="source.path"><a :href="route(source.path)">{{ source.title }}</a></li></ul>
    </details>
  </section>
</template>
