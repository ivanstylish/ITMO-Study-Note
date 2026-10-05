import DefaultTheme from 'vitepress/theme';
import MermaidDiagram from './MermaidDiagram.vue';
import MarkmapDiagram from './MarkmapDiagram.vue';
import CourseExplorer from './CourseExplorer.vue';
import StudyHero from './StudyHero.vue';
import Backlinks from './Backlinks.vue';
import { h } from 'vue';
import { useData } from 'vitepress';
import './style.css';

export default {
  extends: DefaultTheme,
  Layout: {
    setup() {
      const { page } = useData();
      return () => h(DefaultTheme.Layout, null, {
        'doc-top': () => page.value.relativePath === 'index.md' ? h(StudyHero) : null,
        'doc-after': () => h(Backlinks)
      });
    }
  },
  enhanceApp({ app }) {
    app.component('MermaidDiagram', MermaidDiagram);
    app.component('MarkmapDiagram', MarkmapDiagram);
    app.component('CourseExplorer', CourseExplorer);
  }
};
