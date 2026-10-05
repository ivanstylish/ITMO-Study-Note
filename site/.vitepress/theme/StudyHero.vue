<script setup>
import { withBase } from 'vitepress';
import catalog from '../../../navigation/catalog.json';
const current = Math.max(...catalog.semesters.map(s => s.number));
const archived = catalog.courses.filter(c => c.semesters.every(n => n < current)).length;
const active = catalog.courses.filter(c => c.semesters.includes(current)).length;
const entries = [
  { number: '01', title: '学期与课程', detail: '讲义、实验、报告与考试资料', href: '/navigation/courses.html' },
  { number: '02', title: '考前复习', detail: '从速查回到原理与实现', href: '/study/revision.html' },
  { number: '03', title: '复习脑图', detail: '展开课程，串起学习方向', href: '/knowledge/mindmap.html' },
  { number: '04', title: '知识关联', detail: '概念、资料与引用来源', href: '/knowledge/index.html' }
];
</script>

<template>
  <section class="study-hero" aria-label="学习知识库导航">
    <p class="study-eyebrow">ITMO · LEARNING LIBRARY</p>
    <h2>让每一门课，<br><span>连成一条复习路线。</span></h2>
    <p class="study-hero-description">课程资料、实验记录与知识关联，都从这里出发。</p>
    <div class="study-metrics">
      <span><strong>{{ archived }}</strong> 门归档课程</span>
      <span><strong>{{ active }}</strong> 门本学期课程</span>
      <span><strong>5</strong> 个学习方向</span>
    </div>
    <div class="study-entry-grid">
      <a v-for="entry in entries" :key="entry.href" :href="withBase(entry.href)" class="study-entry">
        <span class="study-entry-number" aria-hidden="true">{{ entry.number }}</span>
        <strong>{{ entry.title }} <span aria-hidden="true">↗</span></strong>
        <span>{{ entry.detail }}</span>
      </a>
    </div>
  </section>
</template>
