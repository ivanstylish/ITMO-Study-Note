import DefaultTheme from 'vitepress/theme';
import MermaidDiagram from './MermaidDiagram.vue';
import MarkmapDiagram from './MarkmapDiagram.vue';
import CourseExplorer from './CourseExplorer.vue';
import AcademicYears from './AcademicYears.vue';
import Backlinks from './Backlinks.vue';
import { h } from 'vue';
import './style.css';

export default {
  extends: DefaultTheme,
  Layout: {
    setup() {
      return () => h(DefaultTheme.Layout, null, {
        'doc-after': () => h(Backlinks)
      });
    }
  },
  enhanceApp({ app }) {
    app.component('MermaidDiagram', MermaidDiagram);
    app.component('MarkmapDiagram', MarkmapDiagram);
    app.component('CourseExplorer', CourseExplorer);
    app.component('AcademicYears', AcademicYears);
  }
};
