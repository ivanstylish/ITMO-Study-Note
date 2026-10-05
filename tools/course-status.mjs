export const statusLabels = Object.freeze({ passed: '✓ 已通过', pending: '○ 待通过', unmarked: '— 未标记' });
export const statusKeys = Object.keys(statusLabels);
export const statusLabel = key => statusLabels[key || 'unmarked'] || statusLabels.unmarked;

export function courseStatus(course, semester) {
  return statusLabel(semester == null ? course.status : course.semesterStatus?.[semester] || course.status);
}

export function courseStatusSummary(course) {
  const groups = new Map();
  for (const semester of course.semesters) {
    const label = courseStatus(course, semester);
    if (!groups.has(label)) groups.set(label, []);
    groups.get(label).push(semester);
  }
  if (groups.size === 1) return [...groups.keys()][0];
  return [...groups].map(([label, semesters]) => `第 ${semesters.join('、')} 学期：${label}`).join(' · ');
}

export function labStatus(course, entry, manual) {
  const number = entry.label.replace(/[–—]/g, '-').match(/(?:lab(?:work)?|лаб(?:ораторная)?)\s*([0-9]+(?:[.-][0-9]+)?)/i)?.[1];
  return manual?.statuses.get(number) || manual?.resourceStates.get(entry.path) || statusLabel(entry.status || course.status);
}
