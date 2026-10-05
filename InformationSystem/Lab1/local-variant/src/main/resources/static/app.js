'use strict';
const $ = (id) => document.getElementById(id);
const names = { cities: 'Города', coordinates: 'Координаты', humans: 'Губернаторы' };
const enums = {
    climate: ['RAIN_FOREST', 'MONSOON', 'TROPICAL_SAVANNA', 'MEDITERRANIAN'],
    government: ['ANARCHY', 'DESPOTISM', 'ETHNOCRACY'],
    standardOfLiving: ['ULTRA_HIGH', 'VERY_HIGH', 'LOW', 'VERY_LOW', 'NIGHTMARE']
};
let session;
let tab = 'home';
let page = 0;
let total = 0;
let points = [];
let people = [];
let revision = null;
let polling = false;
let renderId = 0;
let dialogState = null;
let lastOperation = null;
let lastPollingError = null;
let filter = { column: '', value: '', sort: 'id', desc: 'false' };

// 动态文本先转义 HTML 特殊字符，再放入页面，避免用户输入被当作标签执行。
function esc(value) {
    const entities = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
    return String(value ?? '—').replace(/[&<>"']/g, (character) => entities[character]);
}

// 统一发送 JSON 请求，并附带当前会话的 CSRF 令牌；失败交给调用处显示错误弹窗。
async function api(path, options = {}) {
    const response = await fetch('/api' + path, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...(session ? { [session.header]: session.token } : {}),
            ...options.headers
        }
    });
    if (response.status === 401) {
        location.href = '/login';
        throw Error('Сессия завершена');
    }
    const text = await response.text();
    let data;
    try {
        data = text ? JSON.parse(text) : null;
    } catch {
        throw Error('Неверный ответ сервера');
    }
    if (!response.ok) {
        const error = Error(data?.message || 'Ошибка HTTP ' + response.status);
        error.fields = data?.fields;
        error.status = response.status;
        throw error;
    }
    return data;
}
const heading = (key) => key.charAt(0).toUpperCase() + key.slice(1);
const dateKeys = new Set(['birthday', 'creationDate', 'establishmentDate']);
const dateOnly = (value) => (value == null ? '' : String(value).split('T')[0]);
// 查看窗口递归展示关联对象；所有日期仅显示年月日，字段名称首字母大写。
function details(object) {
    const entries = Object.entries(object).filter(([key]) => key !== 'version');
    const rows = entries.map(([key, value]) => {
        const content = value && typeof value === 'object'
            ? details(value)
            : esc(dateKeys.has(key) ? dateOnly(value) || '—' : value);
        return '<dt>' + I18n.html(heading(key)) + '</dt><dd>' + content + '</dd>';
    });
    return '<dl class="details">' + rows.join('') + '</dl>';
}

function showError(error) {
    const message = error instanceof TypeError
        ? 'Нет соединения с сервером. Повторите попытку.'
        : error.message;
    I18n.text($('status'), message);
    $('status').className = 'error';
    UI.error(message);
    I18n.translate($('status'));
}
function actionButtons(id) {
    const safeId = esc(id);
    return '<button data-action="view" data-id="' + safeId + '">' + I18n.html('Просмотр') + '</button>'
        + '<button data-action="edit" data-id="' + safeId + '">' + I18n.html('Изменить') + '</button>'
        + '<button class="danger" data-action="delete" data-id="' + safeId + '">' + I18n.html('Удалить') + '</button>';
}

const tableColumns = {
    cities: [
        'id', 'name', 'coordinates', 'creationDate', 'area', 'population', 'establishmentDate',
        'capital', 'metersAboveSeaLevel', 'climate', 'government', 'standardOfLiving', 'governor'
    ],
    coordinates: ['id', 'x', 'y'],
    humans: ['id', 'name', 'age', 'height', 'birthday']
};

function tableRow(item, columns) {
    const cells = columns.map((key) => {
        let value = item[key];
        if (dateKeys.has(key)) value = dateOnly(value) || null;
        if (key === 'coordinates' && value) {
            value = '#' + value.id + ' (' + value.x + ', ' + value.y + ')';
        }
        if (key === 'governor' && value) value = '#' + value.id + ' ' + value.name;
        return '<td title="' + esc(value) + '">' + esc(value) + '</td>';
    });
    return '<tr>' + cells.join('') + '<td>' + actionButtons(item.id) + '</td></tr>';
}

async function refresh() {
    // 请求编号用于丢弃过期响应，防止快速切换面板时显示上一个面板的数据。
    const request = ++renderId;
    const selectedTab = tab;
    if (selectedTab === 'operations' || selectedTab === 'home') return;
    const pageSize = Number($('size').value);
    let items;
    if (selectedTab === 'cities') {
        const query = new URLSearchParams({ ...filter, page, size: $('size').value });
        const result = await api('/cities?' + query);
        if (request !== renderId) return;
        total = result.total;
        if (page > 0 && page * pageSize >= total) {
            page = Math.max(0, Math.ceil(total / pageSize) - 1);
            return refresh();
        }
        items = result.items;
    } else {
        const all = await api('/' + selectedTab);
        if (request !== renderId) return;
        total = all.length;
        page = Math.min(page, Math.max(0, Math.ceil(total / pageSize) - 1));
        items = all.slice(page * pageSize, (page + 1) * pageSize);
    }
    const columns = tableColumns[selectedTab];
    const headers = columns.map((key) => '<th>' + I18n.html(heading(key)) + '</th>').join('');
    $('head').innerHTML = '<tr>' + headers + '<th>' + I18n.html('Действия') + '</th></tr>';
    $('rows').innerHTML = items.length
        ? items.map((item) => tableRow(item, columns)).join('')
        : '<tr><td colspan="' + (columns.length + 1) + '">' + I18n.html('Объектов нет.') + '</td></tr>';
    const pageCount = Math.max(1, Math.ceil(total / pageSize));
    updatePageInfo(pageCount);
    $('prev').disabled = page === 0;
    $('next').disabled = (page + 1) * pageSize >= total;
    I18n.translate($('workspace'));
}
function updatePageInfo(pageCount = Math.max(1, Math.ceil(total / Number($('size').value)))) {
    $('pageInfo').textContent = I18n.t('Страница {page} / {pages} · Всего: {total}')
        .replace('{page}', page + 1).replace('{pages}', pageCount).replace('{total}', total);
}
window.addEventListener('languagechange', () => updatePageInfo());
function selectTab(value) {
    tab = value;
    page = 0;
    renderId++;
    document.querySelectorAll('[data-tab]').forEach((button) => {
        button.classList.toggle('active', button.dataset.tab === tab);
    });
    $('dashboard').hidden = tab !== 'home';
    $('workspace').hidden = tab === 'home';
    $('objects').hidden = tab === 'operations' || tab === 'home';
    $('operations').hidden = tab !== 'operations';
    $('filters').hidden = tab !== 'cities';
    if (tab !== 'operations' && tab !== 'home') {
        I18n.text($('sectionTitle'), names[tab]);
        refresh().catch(showError);
    }
    window.scrollTo({ top: 0, behavior: 'instant' });
}
const fields = {
    coordinates: [
        ['x', 'Long · обязательно', 'long', true],
        ['y', 'double > -531', 'number', true]
    ],
    humans: [
        ['name', 'Имя', 'text', true],
        ['age', 'Возраст > 0', 'int', true],
        ['height', 'Рост > 0', 'number', true],
        ['birthday', 'Дата рождения', 'date', false]
    ],
    cities: [
        ['name', 'Название', 'text', true],
        ['coordinatesId', 'Существующие координаты', 'point', true],
        ['area', 'Площадь > 0', 'number', true],
        ['population', 'Население > 0', 'long', true],
        ['establishmentDate', 'Дата основания', 'date', false],
        ['capital', 'Столица', 'boolean', true],
        ['metersAboveSeaLevel', 'Высота над уровнем моря', 'long', false],
        ['climate', 'Климат', 'enum', false],
        ['government', 'Форма правления', 'enum', false],
        ['standardOfLiving', 'Уровень жизни', 'enum', true],
        ['governorId', 'Существующий губернатор', 'human', false]
    ]
};
function inputHtml(field, object) {
    const [key, label, type, required] = field;
    let value = object[key];
    if (key === 'coordinatesId') value = object.coordinates?.id;
    if (key === 'governorId') value = object.governor?.id;
    if (type === 'date') value = dateOnly(value);
    let choices;
    if (type === 'enum') choices = enums[key].map((x) => [x, x]);
    if (type === 'point') choices = points.map((p) => [p.id, '#' + p.id + ' (' + p.x + ', ' + p.y + ')']);
    if (type === 'human') choices = people.map((p) => [p.id, '#' + p.id + ' ' + p.name]);
    if (type === 'boolean') {
        choices = [
            ['false', 'Нет'],
            ['true', 'Да']
        ];
        value = String(value ?? false);
    }
    let control;
    if (choices) {
        const emptyOption = type !== 'boolean'
            ? '<option value="" data-i18n="' + (required ? 'Выберите…' : 'NULL') + '">'
                + (required ? I18n.t('Выберите…') : 'NULL') + '</option>'
            : '';
        const options = choices.map(([optionValue, text]) => {
            const selected = String(optionValue) === String(value) ? 'selected' : '';
            const marker = type === 'boolean' ? ' data-i18n="' + esc(text) + '"' : '';
            return '<option value="' + esc(optionValue) + '" ' + selected + marker + '>' + esc(text) + '</option>';
        });
        control = '<select name="' + key + '" ' + (required ? 'required' : '') + '>'
            + emptyOption + options.join('') + '</select>';
    } else {
        const inputType = ['long', 'int'].includes(type) ? 'text' : type;
        let constraints = required ? ' required' : '';
        if (type === 'long' || type === 'int') constraints += ' inputmode="numeric" pattern="-?[0-9]+"';
        if (type === 'number') {
            const min = key === 'y' ? '-530.9999999999999' : '0.000000000000000000000000000000000000000000001';
            constraints += ' step="any" min="' + min + '"';
        }
        control = '<input aria-label="' + esc(heading(key)) + '" name="' + key + '" type="' + inputType
            + '" value="' + esc(value ?? '') + '"' + constraints + '>';
        if (type === 'date') {
            const calendarButton = '<button type="button" data-calendar="' + key
                + '" aria-label="Выбрать дату" data-i18n-label="Выбрать дату">▦</button>';
            control = '<span class="date-control">' + control + calendarButton + '</span>';
        }
    }
    const fieldError = '<span class="field-error" data-field="' + key + '"></span>';
    return '<label><span>' + esc(heading(key)) + ' · ' + I18n.html(label) + (required ? ' *' : '') + '</span>'
        + control + fieldError + '</label>';
}

// 表单字段按后端需要的类型转换，转换逻辑与弹窗的显示逻辑分开，便于阅读。
function editorPayload(type, form, object) {
    const input = Object.fromEntries(new FormData(form));
    const payload = {};
    for (const [key, label, kind, required] of fields[type]) {
        const value = input[key];
        if (value === '') {
            if (required) throw Error(key + ': обязательное поле');
            payload[key] = null;
            continue;
        }
        if (['long', 'int', 'point', 'human'].includes(kind)) {
            // JavaScript 的 Number 只能精确表示 53 位整数；Long 使用 BigInt 校验并以字符串发送。
            if (!/^-?\d+$/.test(value)) throw Error(heading(key) + ': введите целое число.');
            const number = BigInt(value);
            const min = kind === 'int' ? -2147483648n : -9223372036854775808n;
            const max = kind === 'int' ? 2147483647n : 9223372036854775807n;
            if (number < min || number > max) throw Error(key + ': число вне диапазона ' + kind);
            payload[key] = kind === 'int' ? Number(number) : number.toString();
        } else if (kind === 'number') {
            const number = Number(value);
            if (!Number.isFinite(number)) throw Error(key + ': требуется конечное число');
            payload[key] = number;
        } else if (kind === 'boolean') {
            payload[key] = value === 'true';
        } else if (kind === 'date') {
            // 界面只选日期，但 API 保留实验规定的时间类型；日期未改动时保留原始时间。
            const midnight = key === 'birthday' ? 'T00:00:00Z' : 'T00:00:00';
            payload[key] = dateOnly(object[key]) === value ? object[key] : value + midnight;
        } else {
            payload[key] = value;
        }
    }
    return payload;
}

async function openDialog(mode, id) {
    const type = tab;
    const object = id ? await api('/' + type + '/' + id) : {};
    if (type === 'cities' && ['edit', 'create'].includes(mode)) {
        [points, people] = await Promise.all([api('/coordinates'), api('/humans')]);
    }
    dialogState = { type, mode, id, object };
    I18n.text($('dialogNotice'), '');
    $('dialogNotice').classList.remove('error');
    const modeName = { view: 'Просмотр', edit: 'Изменение', create: 'Создание', delete: 'Удаление' }[mode];
    I18n.text($('dialogTitle'), modeName + ' · ' + names[type] + (id ? ' #' + id : ''));
    if (mode === 'view') {
        $('dialogBody').innerHTML = '<div id="objectDetails">' + details(object) + '</div>'
            + '<div class="actions"><button id="viewEdit" class="primary">' + I18n.html('Изменить') + '</button></div>';
        $('viewEdit').onclick = () => openDialog('edit', id).catch(showError);
    } else if (mode === 'delete') {
        $('dialogBody').innerHTML = '<p>' + I18n.html('Удалить объект') + ' #' + esc(id)
            + '? ' + I18n.html('Операция будет отклонена, если на него ссылаются другие объекты.') + '</p>'
            + '<div class="error-box" id="formError"></div>'
            + '<div class="actions"><button id="confirmDelete" class="danger">' + I18n.html('Подтвердить удаление') + '</button></div>';
        $('confirmDelete').onclick = async () => {
            $('confirmDelete').disabled = true;
            try {
                const path = '/' + type + '/' + id + '?version=' + encodeURIComponent(object.version);
                await api(path, { method: 'DELETE' });
                $('dialog').close();
                await refresh();
            } catch (e) {
                I18n.text($('formError'), e.message);
                UI.error(e.message);
            } finally {
                if ($('confirmDelete')) $('confirmDelete').disabled = false;
                I18n.translate($('dialog'));
            }
        };
    } else {
        const notice = type === 'cities'
            ? 'id и creationDate генерируются автоматически. Сначала создайте координаты / губернатора через меню. '
                + 'Один объект можно связать с несколькими городами.'
            : 'Изменение общего объекта отразится во всех связанных городах.';
        const inputs = fields[type].map((field) => inputHtml(field, object)).join('');
        $('dialogBody').innerHTML = '<p>' + I18n.html(notice) + '</p><form id="editor" novalidate>'
            + '<div class="form-grid">' + inputs + '</div><div class="error-box" id="formError"></div>'
            + '<div class="actions"><button class="primary" id="save">' + I18n.html('Сохранить') + '</button></div></form>';
        $('editor').onsubmit = async (event) => {
            event.preventDefault();
            if (!UI.validate(event.target)) return;
            I18n.text($('formError'), '');
            document.querySelectorAll('.field-error').forEach((e) => (I18n.text(e, '')));
            try {
                const payload = editorPayload(type, event.target, object);
                if (id) payload.version = object.version;
                $('save').disabled = true;
                await api('/' + type + (id ? '/' + id : ''), {
                    method: id ? 'PUT' : 'POST',
                    body: JSON.stringify(payload)
                });
                $('dialog').close();
                await refresh();
            } catch (e) {
                I18n.text($('formError'), e.message);
                UI.error([e.message, ...Object.values(e.fields || {})].join('\n'));
                if (e.fields) {
                    Object.entries(e.fields).forEach(([key, message]) => {
                        const span = document.querySelector('[data-field="' + key + '"]');
                        if (span) I18n.text(span, message);
                    });
                }
            } finally {
                if ($('save')) $('save').disabled = false;
                I18n.translate($('dialog'));
            }
        };
    }
    document.querySelectorAll('[data-calendar]').forEach((button) => {
        button.onclick = () => {
            const input = document.querySelector('[name="' + button.dataset.calendar + '"]');
            try {
                if (input.showPicker) input.showPicker();
                else input.focus();
            } catch {
                input.focus();
            }
        };
    });
    I18n.translate($('dialog'));
    if (!$('dialog').open) $('dialog').showModal();
}
async function runSpecial(operation, needle) {
    const result = await api('/operations/' + operation + '?' + new URLSearchParams({ needle }));
    const value = result.value;
    $('specialResult').removeAttribute('data-i18n');
    $('specialResult').classList.remove('error');
    if (operation === 'groups') {
        const rows = value.map((row) => '<tr><td>' + esc(row.area) + '</td><td>' + esc(row.count) + '</td></tr>');
        const header = '<div class="table-wrap"><table><thead><tr><th>' + I18n.html('Area')
            + '</th><th>' + I18n.html('Count') + '</th></tr></thead><tbody>';
        $('specialResult').innerHTML = value.length
            ? header + rows.join('') + '</tbody></table></div>'
            : I18n.html('Городов пока нет.');
    } else if (operation === 'substring') {
        const cards = value.map((city) => {
            const title = esc(city.name) + ' · Id ' + esc(city.id);
            return '<details><summary>' + title + '</summary>' + details(city) + '</details>';
        });
        $('specialResult').innerHTML = value.length ? cards.join('') : I18n.html('Совпадений нет.');
    } else {
        const label =
            operation === 'average' ? 'Средняя высота над уровнем моря' : 'Длина маршрута';
        $('specialResult').innerHTML =
            '<p class="eyebrow">' + I18n.html(label) + '</p><h2>' + (value == null ? I18n.html('Нет данных') : esc(value)) + '</h2>';
    }
    I18n.translate($('specialResult'));
}
function specialError(error) {
    I18n.text($('specialResult'), error.message);
    $('specialResult').classList.add('error');
    UI.error(error.message);
    I18n.translate($('specialResult'));
}
document
    .querySelectorAll('[data-tab]')
    .forEach((b) => (b.onclick = () => selectTab(b.dataset.tab)));
$('create').onclick = () => openDialog('create').catch(showError);
$('close').onclick = () => $('dialog').close();
$('dialog').addEventListener('close', () => {
    dialogState = null;
});
$('rows').onclick = (e) => {
    const b = e.target.closest('button[data-action]');
    if (b) openDialog(b.dataset.action, b.dataset.id).catch(showError);
};
$('lookup').onsubmit = (e) => {
    e.preventDefault();
    if (!UI.validate(e.target)) return;
    openDialog('view', new FormData(e.target).get('id')).catch(showError);
};
$('filters').onsubmit = (e) => {
    e.preventDefault();
    filter = {
        column: $('column').value,
        value: $('filterValue').value,
        sort: $('sort').value,
        desc: $('desc').value
    };
    page = 0;
    refresh().catch(showError);
};
$('prev').onclick = () => {
    page--;
    refresh().catch(showError);
};
$('next').onclick = () => {
    page++;
    refresh().catch(showError);
};
$('size').onchange = () => {
    page = 0;
    refresh().catch(showError);
};
$('specialForm').onsubmit = (e) => {
    e.preventDefault();
    lastOperation = { operation: $('operation').value, needle: $('needle').value };
    runSpecial(lastOperation.operation, lastOperation.needle).catch(specialError);
};
$('logout').onclick = async () => {
    try {
        const response = await fetch('/logout', {
            method: 'POST',
            headers: { [session.header]: session.token }
        });
        if (!response.ok) throw Error('Не удалось выйти. Обновите страницу.');
        location.href = '/login';
    } catch (e) {
        showError(e);
    }
};
async function tick() {
    // 保留两秒轮询和数据库 revision 检查；编辑中的表单不被自动刷新覆盖。
    if (polling) return;
    polling = true;
    try {
        const current = (await api('/revision')).revision;
        if (current !== revision) {
            await refresh();
            if (tab === 'operations' && lastOperation)
                await runSpecial(lastOperation.operation, lastOperation.needle).catch(specialError);
            if (dialogState && revision !== null) {
                const state = dialogState;
                if (state.mode === 'view') {
                    try {
                        const latest = await api('/' + state.type + '/' + state.id);
                        if (dialogState === state) $('objectDetails').innerHTML = details(latest);
                    } catch (e) {
                        if (dialogState === state) {
                            I18n.text($('dialogNotice'),
                                e.status === 404
                                    ? 'Этот объект удалён другим пользователем.'
                                    : e.message);
                            $('dialogNotice').classList.add('error');
                            UI.error(e.status === 404 ? 'Этот объект удалён другим пользователем.' : e.message);
                        }
                    }
                } else {
                    I18n.text($('dialogNotice'),
                        'Данные в системе обновлены. Введённые значения сохранены в форме. При конфликте закройте окно и откройте объект заново.');
                }
            }
            revision = current;
        }
        $('status').className = '';
        I18n.text($('status'), '● Соединение активно');
        lastPollingError = null;
    } catch (e) {
        I18n.text($('status'), 'Нет соединения с сервером.');
        $('status').className = 'error';
        if (lastPollingError !== e.message) {
            lastPollingError = e.message;
            showError(e);
        }
    } finally {
        I18n.translate($('status'));
        I18n.translate($('dialogNotice'));
        polling = false;
    }
}
(async () => {
    try {
        session = await api('/session');
        $('user').textContent = session.username;
        await tick();
        setInterval(tick, 2000);
    } catch (e) {
        showError(e);
    }
})();
