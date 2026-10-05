<script setup>
import { computed, ref } from 'vue';
import { withBase } from 'vitepress';
import catalog from '../../../navigation/catalog.json';
import { courseStatusSummary, courseStatus } from '../../../tools/course-status.mjs';
const current = Math.max(...catalog.semesters.map(s => s.number));
const stage = ref('current');
const query = ref('');
const stages = [
  { id: 'current', title: '本学期', count: catalog.courses.filter(c => c.semesters.includes(current)).length },
  { id: 'archived', title: '归档课程', count: catalog.courses.filter(c => c.semesters.every(n => n < current)).length },
  { id: 'all', title: '全部课程', count: catalog.courses.length }
];
const courses = computed(() => {
  const text = query.value.trim().toLocaleLowerCase();
  return catalog.courses.filter(c => (stage.value === 'all' || (stage.value === 'current' ? c.semesters.includes(current) : c.semesters.every(n => n < current)))
    && (!text || `${c.title} ${c.ru} ${c.kind} ${c.directory}`.toLocaleLowerCase().includes(text)));
});
const status = course => stage.value === 'current' ? courseStatus(course, current) : courseStatusSummary(course);
const route = course => withBase('/' + course.dashboard.slice(0, -3).split('/').map(encodeURIComponent).join('/') + '.html');
const counts = { theory: '讲义', labs: '实验', defense: '答辩', exam: '考试' };
</script>

<template>
  <section class="course-explorer" aria-label="查找课程">
    <div class="course-controls">
      <div class="course-stage-buttons" role="group" aria-label="按学习阶段筛选">
        <button v-for="item in stages" :key="item.id" type="button" :aria-pressed="stage === item.id" @click="stage = item.id">
          {{ item.title }} <span>{{ item.count }}</span>
        </button>
      </div>
      <label class="course-search"><span>查找课程</span><input v-model="query" type="search" placeholder="中文、俄文或课程名称"></label>
    </div>
    <p class="course-result-count" role="status">{{ courses.length }} 门课程</p>
    <div v-if="courses.length" class="course-card-grid">
      <a v-for="course in courses" :key="course.id" :href="route(course)" class="course-card">
        <div class="course-card-top"><span>第 {{ course.semesters.join('、') }} 学期</span><span aria-hidden="true">↗</span></div>
        <h3>{{ course.title }}</h3>
        <p lang="ru">{{ course.ru }}</p>
        <span class="study-status" :class="course.status">{{ status(course) }}</span>
        <div class="course-resource-tags">
          <template v-for="(label, key) in counts" :key="key"><span v-if="course.resources[key]?.length">{{ label }} {{ course.resources[key].length }}</span></template>
        </div>
      </a>
    </div>
    <p v-else class="course-empty">没有找到对应课程，试试另一种语言或切换学习阶段。</p>
  </section>
</template>
