"""Графики SVG средствами стандартной библиотеки; без библиотек визуализации."""
from html import escape
from math import log10

NAMES = ['Берем.', 'Глюкоза', 'Давление', 'Кожа', 'Инсулин', 'ИМТ', 'Наслед.', 'Возраст', 'Диабет']
COLORS = ['#245d98', '#c34433', '#288264', '#8155a6']


def panel(title, labels, series, logarithmic=False, bars=False, limits=None):
    """Одна панель 640 × 370 с подписями осей и общей легендой."""
    values = [float(v) for _, row in series for v in row]
    low, high = limits or (min(values), max(values))
    if limits is None:
        padding = (high - low) * 0.12 or 1
        low, high = (0 if bars else low - padding), high + padding
    xs = [log10(float(x)) for x in labels] if logarithmic else list(range(len(labels)))
    xspan = max(xs) - min(xs) or 1
    xs = [65 + 515 * (x - min(xs)) / xspan for x in xs]
    if bars:
        xs = [75 + i * 515 / len(labels) for i in range(len(labels))]
    yy = lambda v: 275 - 215 * (float(v) - low) / (high - low)
    parts = [f'<text x="22" y="25" font-size="20" font-weight="bold">{escape(title)}</text>']
    for i in range(5):
        value = low + (high - low) * i / 4
        y = yy(value)
        parts += [f'<path d="M60,{y:.2f}H600" stroke="#dce2e8"/>',
                  f'<text x="52" y="{y + 5:.2f}" text-anchor="end">{value:.3g}</text>']
    for x, label in zip(xs, labels):
        parts.append(f'<text transform="translate({x:.2f},298) rotate(22)" font-size="17">{escape(str(label))}</text>')
    for j, (name, values) in enumerate(series):
        color = COLORS[j % len(COLORS)]
        if bars:
            for x, v in zip(xs, values):
                y = yy(v)
                parts.append(f'<rect x="{x-12:.2f}" y="{y:.2f}" width="24" height="{max(0,yy(0)-y):.2f}" fill="{color}"/>')
        else:
            points = ' '.join(f'{x:.2f},{yy(v):.2f}' for x, v in zip(xs, values))
            parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2.5"/>')
        if len(series) > 1:
            parts += [f'<path d="M{65+j*137},347h20" stroke="{color}" stroke-width="3"/>',
                      f'<text x="{90+j*137}" y="352">{escape(name)}</text>']
    return ''.join(parts)


def save(path, panels, columns=2):
    rows = (len(panels) + columns - 1) // columns
    body = ''.join(f'<g transform="translate({i%columns*640},{i//columns*370})">{p}</g>' for i, p in enumerate(panels))
    path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{columns*640}" height="{rows*370}" viewBox="0 0 {columns*640} {rows*370}"><rect width="100%" height="100%" fill="white"/><g font-family="Arial" font-size="19" fill="#172b4d">{body}</g></svg>', encoding='utf-8')


def make_figures(out, statistics, results, curves):
    folder = out / 'figures'
    folder.mkdir(exist_ok=True)
    titles = ['Количество', 'Среднее', 'Стандартное отклонение', 'Минимум',
              'Первый квартиль', 'Медиана', 'Третий квартиль', 'Максимум']
    panels = [panel(title, NAMES, [(title, statistics[column])], bars=True)
              for title, column in zip(titles, ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max'])]
    save(folder / 'statistics.svg', panels)
    rates, iterations = [0.001, 0.01, 0.1, 1.0], [5, 20, 100, 500, 2000]
    for method in ['gd', 'newton']:
        subset = results[results.method == method]
        panels = [panel(title, iterations, [(f'α={rate:g}', subset[subset.rate == rate]['test_' + key]) for rate in rates],
                        logarithmic=True, limits=(0.45, 0.85))
                  for title, key in [('Доля верных ответов', 'accuracy'), ('Точность', 'precision'), ('Полнота', 'recall'), ('F1-мера', 'f1')]]
        save(folder / f'{method}_metrics.svg', panels)
    steps = [0, 1, 5, 20, 50, 100, 200, 500, 1000, 2000]
    panels = [panel(title, [max(1, t) for t in steps[1:]],
                    [(f'α={rate:g}', [curves[(method, rate)][t] for t in steps[1:]]) for rate in rates],
                    logarithmic=True, limits=(0.4, 0.7))
              for method, title in [('gd', 'Градиентный спуск'), ('newton', 'Метод Ньютона')]]
    save(folder / 'loss.svg', panels)
