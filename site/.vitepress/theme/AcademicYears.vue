<script setup>
import { withBase } from 'vitepress';
import catalog from '../../../navigation/catalog.json';
import { academicYears } from '../../../tools/academic-home.mjs';
import { courseStatus } from '../../../tools/course-status.mjs';
const years=academicYears(catalog);
const route=file=>withBase('/'+file.replace(/\.md$/,'.html').split('/').map(encodeURIComponent).join('/'));
</script>

<template>
  <div class="academic-years">
    <section v-for="year in years" :key="year.number" class="academic-year" :aria-labelledby="'year-'+year.number">
      <header class="academic-year-header">
        <h2 :id="'year-'+year.number"><span aria-hidden="true">0{{ year.number }}</span>{{ year.title }}</h2>
        <span>{{ year.period }}</span>
      </header>
      <div class="academic-semesters">
        <section v-for="semester in year.semesters" :key="semester.number" class="academic-semester" :aria-labelledby="'semester-'+semester.number">
          <h3 :id="'semester-'+semester.number">
            <a v-if="semester.record" :href="route(`academic/semester-${String(semester.number).padStart(2,'0')}.md`)">第 {{ semester.number }} 学期 <span aria-hidden="true">↗</span></a>
            <template v-else>第 {{ semester.number }} 学期</template>
          </h3>
          <ul v-if="semester.courses.length" class="academic-course-list">
            <li v-for="course in semester.courses" :key="course.id">
              <a :href="route(course.dashboard)">
                <span class="academic-course-title">{{ course.title }}<span class="study-status" :class="course.semesterStatus?.[semester.number] || course.status">{{ courseStatus(course,semester.number) }}</span></span>
                <span class="academic-course-ru" lang="ru">{{ course.ru }}</span>
              </a>
            </li>
          </ul>
          <p v-else class="academic-empty">本学期课程资料尚未收录。</p>
        </section>
      </div>
    </section>
  </div>
</template>
