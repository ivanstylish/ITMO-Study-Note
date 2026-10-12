from pathlib import Path
from collections import defaultdict
import csv
import difflib
import hashlib
import importlib.util
import json
import math
import re
import statistics
from datetime import datetime, timezone, timedelta

root = Path(__file__).resolve().parents[1]
lab = root.parent
analysis = root / 'analysis'
analysis.mkdir(exist_ok=True)
source = (root / 'faithful/report.typ').read_text(encoding='utf-8')
changes = [
('Отдельная запись гипотезы до запуска в переданных файлах отсутствует; далее она проверяется без утверждения о предварительной регистрации.',
 'Предварительная фиксация гипотезы в журналах эксперимента не зарегистрирована; проверка относится к сохранённым результатам.'),
('*Ссылка на выполненную работу:* персональный PR или коммит не предоставлен. Исходная постановка:',
 '*Материалы работы:* #link("https://github.com/ivanstylish/xv6-riscv/tree/main/course-code/lab/intro-exp")[ivanstylish/xv6-riscv — course-code/lab/intro-exp]. Исходная постановка:'),
('Предварительная пилотная серия и расчёт N до сбора данных не представлены.',
 'Пилотная оценка дисперсии и предварительный расчёт N в протоколе не зафиксированы.'),
('В переданных данных запись занимает больше времени в обеих реализациях.',
 'Согласно сохранённым измерениям, обновление данных занимает больше времени в обеих реализациях.'),
(' Автор сообщил о просмотре данных через cat, без редактирования.', ''),
('*Более важная следующая проверка — согласованность часов и накладные расходы коротких запусков*, а не механическое увеличение N.',
 '*Дополнительная оценка надёжности должна учитывать согласованность часов и накладные расходы коротких запусков.*'),
('Неполная поддержка событий perf и окончательная трактовка расхождения часов должны учитываться при защите; вымышленные значения в отчёт не включены.',
 'Неполная поддержка событий perf и расхождение часов ограничивают интерпретацию результатов; недоступные показатели не представлены как числовые измерения.'),
('Источник: `diag-short-20260928-235755-16397`, STAGE=all. Проверены 24 записи',
 'Источник: `diag-short-20260928-235755-16397`, STAGE=all. Диагностическая серия содержит 24 проверенные записи'),
]
revised = source
for before, after in changes:
    if revised.count(before) != 1:
        raise ValueError('Expected one prose replacement: ' + before)
    revised = revised.replace(before, after)

def blocks(text, start, end):
    output = []
    position = 0
    while (position := text.find(start, position)) >= 0:
        finish = text.find(end, position) + len(end)
        if finish < len(end):
            raise ValueError('Unterminated block')
        output.append(text[position:finish])
        position = finish
    return output

table_pattern = r'^#table\([\s\S]*?^\s*\)\s*$'
figure_pattern = r'^#figure\([^\n]*\n[^\n]*'
assert re.findall(table_pattern,source,re.M) == re.findall(table_pattern,revised,re.M)
assert re.findall(figure_pattern,source,re.M) == re.findall(figure_pattern,revised,re.M)
(root / 'revised/report.typ').write_text(revised, encoding='utf-8', newline='\n')
(root / 'analysis/prose-changes.diff').write_text(''.join(difflib.unified_diff(source.splitlines(True),
    revised.splitlines(True), fromfile='faithful/report.typ', tofile='revised/report.typ')), encoding='utf-8')
(root / 'analysis/prose-changes.json').write_text(json.dumps([{'before': a, 'after': b} for a, b in changes],
    ensure_ascii=False, indent=2), encoding='utf-8')

def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))

quantile_file = lab / 'intro-exp-recovery-audit-20261012/analysis/statistics/analyze_existing_data.py'
spec = importlib.util.spec_from_file_location('existing_statistics', quantile_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def describe(rows, unit='wall_s'):
    values = [float(row[unit]) for row in rows]
    n = len(values)
    mean = statistics.mean(values)
    sd = statistics.stdev(values) if n > 1 else None
    half = module.student_quantile(n - 1) * sd / math.sqrt(n) if n > 1 else None
    return {'n': n, 'mean_s': mean, 'sd_s': sd, 'ci95_low_s': mean-half if half is not None else None,
            'ci95_high_s': mean+half if half is not None else None,
            'sum_s': sum(values), 'min_s': min(values), 'max_s': max(values)}

new_dir = root / 'data/diag-20261012-173446'
old_dir = lab / 'report-data/final-review/diag-short-20260928-235755-16397'
oct7_dir = lab / 'report-data/final-review/diag-short-20261007-162239-485'
new_load = read_csv(new_dir / 'load.csv')
old_load = read_csv(old_dir / 'load.csv')
new_tools = read_csv(new_dir / 'tool_overhead.csv')
oct7_tools = read_csv(oct7_dir / 'measurements.csv')
assert len(new_load) == 20 and len(new_tools) == 40
assert {int(row['rep']) for row in new_load} == set(range(1, 11))
new_groups = {condition: [r for r in new_load if r['condition'] == condition] for condition in ('quiet','stress')}
old_groups = {(api, condition): [r for r in old_load if r['api'] == api and r['condition'] == condition]
              for api in ('read_lseek','mmap') for condition in ('quiet','stress')}
comparison = []
for condition in ('quiet','stress'):
    for version, rows, protocol in [('report_20260928', old_groups['read_lseek',condition], 'one_same_cpu_bash_loop_after_preparation'),
                                    ('new_20261012', new_groups[condition], 'cpu2_io1_vm1_256M_before_preparation')]:
        record = {'version': version, 'api': 'read_lseek', 'condition': condition, 'iterations':20,
                  'protocol':protocol, **describe(rows)}
        for metric in ('user_s','sys_s','invol_ctx','minflt','majflt'):
            record['mean_' + metric] = statistics.mean(float(row[metric]) for row in rows)
        comparison.append(record)
tool_summary = []
for api in ('read_lseek','mmap'):
    for tool in ('bare','strace'):
        for version, rows in [('new_20261012',[r for r in new_tools if r['api'] == api and r['tool']==tool]),
                               ('report_appendix_20261007',[r for r in oct7_tools if r['api']==api and r['mode']=='read' and r['tool']==tool])]:
            tool_summary.append({'version':version,'api':api,'tool':tool,'iterations':1,**describe(rows)})

quiet = {int(r['rep']):float(r['wall_s']) for r in new_groups['quiet']}
stress = {int(r['rep']):float(r['wall_s']) for r in new_groups['stress']}
paired = describe([{'wall_s':stress[rep]-quiet[rep]} for rep in range(1,11)])
metadata = json.loads((new_dir / 'file-metadata.json').read_text())
start = metadata['C_top_during_stress.txt']['mtime_epoch']
end = metadata['load.csv']['mtime_epoch']
elapsed = end-start
measured_sum = sum(float(r['wall_s']) for r in new_load)
result = {'comparison': comparison, 'tool_comparison':tool_summary,
    'paired_new_stress_minus_quiet':paired,
    'new_stress_over_quiet':describe(new_groups['stress'])['mean_s']/describe(new_groups['quiet'])['mean_s'],
    'old_stress_over_quiet':describe(old_groups['read_lseek','stress'])['mean_s']/describe(old_groups['read_lseek','quiet'])['mean_s'],
    'new_tool_strace_over_bare':{api:describe([r for r in new_tools if r['api']==api and r['tool']=='strace'])['mean_s']/
                                     describe([r for r in new_tools if r['api']==api and r['tool']=='bare'])['mean_s'] for api in ('read_lseek','mmap')},
    'clock_labels':{'c_top_moscow':metadata['C_top_during_stress.txt']['mtime_moscow'],
                    'last_csv_moscow':metadata['load.csv']['mtime_moscow'],
                    'calendar_interval_s':elapsed,'measured_program_intervals_sum_s':measured_sum,
                    'calendar_minus_measured_s':elapsed-measured_sum,
                    'warning':'calendar labels only; no whole-C monotonic timer or segmented preparation timings'},
    'api_provenance':'default LOAD_API=read_lseek and resource profile; no explicit API column or environment record',
    'new_mmap_C':'not_collected_in_this_directory',
    'per_run_log_validation':'only last B and last C logs preserved; full per-run node checks unavailable',
    'new_perf':'not_collected; absent in tool CSV and A directory; does not invalidate Oct7 separate-binary measurements',
    'prose_only_revision':{'table_blocks_identical':True,'figure_calls_identical':True,
                          'replacement_count':len(changes),'new_C_data_added_to_pdf':False},
    'source_hashes':{str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in
       [new_dir/'load.csv',new_dir/'tool_overhead.csv',old_dir/'load.csv',oct7_dir/'measurements.csv',lab/'report.typ',lab/'Intro-Exp-实验报告-复核版.pdf']}}
(analysis / 'comparison-statistics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
for filename, rows in [('background-comparison.csv',comparison),('tool-comparison.csv',tool_summary)]:
    with (analysis / filename).open('w',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
print(json.dumps({'prose_changes':len(changes),'new_stress_over_quiet':result['new_stress_over_quiet'],
                  'old_stress_over_quiet':result['old_stress_over_quiet'],'c_program_intervals_s':measured_sum,
                  'calendar_C_minutes':elapsed/60,'new_load_groups':{k:describe(v) for k,v in new_groups.items()}},indent=2))
