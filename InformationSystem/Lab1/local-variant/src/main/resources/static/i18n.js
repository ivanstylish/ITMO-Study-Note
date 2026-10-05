'use strict';
// 参考 Programming Lab8 的资源包：t(key) 取文案，语言变化后更新明确标记的控件。
window.I18n = (() => {
    // 数组依次为中文、英文；第三项仅用于把后端英文错误翻译成俄语。
    const words = {
        'CITY — Вход': ['CITY — 登录', 'CITY — Sign in'],
        'CITY — Ваш мир городов': ['CITY — 城市与人', 'CITY — Cities and people'],
        Города: ['城市', 'Cities'],
        'и люди.': ['与人。', 'and people.'],
        Координаты: ['坐标', 'Coordinates'],
        Губернаторы: ['州长', 'Governors'],
        'Специальные операции': ['特殊操作', 'Special operations'],
        Специальные: ['特殊', 'Special'],
        операции: ['操作', 'operations'],
        'На главную': ['返回主页', 'Home'],
        Выйти: ['退出', 'Sign out'],
        Вход: ['登录', 'Sign in'],
        Регистрация: ['注册', 'Register'],
        Войти: ['登录', 'Sign in'],
        'Создать аккаунт': ['创建账号', 'Create account'],
        Аккаунт: ['账号', 'Account'],
        Логин: ['用户名', 'Username'],
        Пароль: ['密码', 'Password'],
        'Повтор пароля': ['确认密码', 'Confirm password'],
        'Повторите пароль': ['确认密码', 'Confirm password'],
        'Введите пароль': ['请输入密码', 'Enter password'],
        'Ещё раз': ['再次输入密码', 'Repeat password'],
        'Ваш логин': ['你的用户名', 'Your username'],
        'Ваш пароль': ['你的密码', 'Your password'],
        'Показать пароль': ['显示密码', 'Show password'],
        'Скрыть пароль': ['隐藏密码', 'Hide password'],
        'Логин: 3–32 латинские буквы, цифры или _. Пароль: от 8 символов.': [
            '用户名：3–32 位英文字母、数字或下划线。密码至少 8 位。',
            'Username: 3–32 Latin letters, digits or _. Password: at least 8 characters.'
        ],
        Фотографии: ['照片来源', 'Photo credits'],
        'Города в кадре': ['城市照片', 'City photographs'],
        Оригинал: ['原图', 'Original'],
        'Wikimedia Commons · фотографии показаны с кадрированием.': [
            'Wikimedia Commons · 照片经过裁切展示。',
            'Wikimedia Commons · photographs are cropped for display.'
        ],
        'Путешествие по городам мира': ['世界城市风光', 'Cities around the world'],
        'городской пейзаж': ['城市风光', 'cityscape'],
        Шанхай: ['上海', 'Shanghai'],
        Москва: ['莫斯科', 'Moscow'],
        Шэньчжэнь: ['深圳', 'Shenzhen'],
        Пекин: ['北京', 'Beijing'],
        'Санкт-Петербург': ['圣彼得堡', 'Saint Petersburg'],
        Лондон: ['伦敦', 'London'],
        Париж: ['巴黎', 'Paris'],
        'Нью-Йорк': ['纽约', 'New York'],
        Берлин: ['柏林', 'Berlin'],
        'Лос-Анджелес': ['洛杉矶', 'Los Angeles'],
        'Разделы приложения': ['功能入口', 'Application sections'],
        'Меню разделов': ['功能菜单', 'Section menu'],
        Создать: ['创建', 'Create'],
        'Id объекта': ['对象 ID', 'Object ID'],
        Найти: ['查找', 'Find'],
        'Точное совпадение': ['完全匹配', 'Exact match'],
        'Без фильтра': ['不筛选', 'No filter'],
        Значение: ['值', 'Value'],
        'С учётом регистра': ['区分大小写', 'Case sensitive'],
        Сортировка: ['排序字段', 'Sort by'],
        Порядок: ['顺序', 'Order'],
        'По возрастанию': ['升序', 'Ascending'],
        'По убыванию': ['降序', 'Descending'],
        Применить: ['应用', 'Apply'],
        Действия: ['操作', 'Actions'],
        'Объектов нет.': ['暂无对象。', 'No objects.'],
        Страница: ['页', 'Page'],
        Всего: ['总计', 'Total'],
        'На странице': ['每页', 'Per page'],
        Назад: ['上一页', 'Previous'],
        Далее: ['下一页', 'Next'],
        Просмотр: ['查看', 'View'],
        Изменить: ['编辑', 'Edit'],
        Изменение: ['编辑', 'Edit'],
        Создание: ['创建', 'Create'],
        Удаление: ['删除', 'Delete'],
        Удалить: ['删除', 'Delete'],
        'Удалить объект': ['删除对象', 'Delete object'],
        'Подтвердить удаление': ['确认删除', 'Confirm deletion'],
        Сохранить: ['保存', 'Save'],
        Закрыть: ['关闭', 'Close'],
        'Операция будет отклонена, если на него ссылаются другие объекты.': [
            '如果其他对象仍引用它，将无法删除。',
            'Deletion is rejected if other objects reference it.'
        ],
        'id и creationDate генерируются автоматически. Сначала создайте координаты / губернатора через меню. Один объект можно связать с несколькими городами.':
            [
                'ID 和创建日期自动生成。先通过菜单创建坐标或市长，同一对象可以关联多个城市。',
                'ID and creation date are generated automatically. Create coordinates or a governor through the menu first. One object can be linked to several cities.'
            ],
        'Изменение общего объекта отразится во всех связанных городах.': [
            '修改共享对象会影响所有关联城市。',
            'Changes to a shared object affect all linked cities.'
        ],
        Имя: ['姓名', 'Name'],
        Название: ['名称', 'Name'],
        'Возраст > 0': ['年龄 > 0', 'Age > 0'],
        'Рост > 0': ['身高 > 0', 'Height > 0'],
        'Дата рождения': ['出生日期', 'Birthday'],
        'Дата основания': ['成立日期', 'Establishment date'],
        'Площадь > 0': ['面积 > 0', 'Area > 0'],
        'Население > 0': ['人口 > 0', 'Population > 0'],
        'Высота над уровнем моря': ['海拔', 'Elevation'],
        'Существующие координаты': ['已有坐标', 'Existing coordinates'],
        'Существующий губернатор': ['已有州长', 'Existing governor'],
        Столица: ['是否首都', 'Capital'],
        Климат: ['气候', 'Climate'],
        'Форма правления': ['政体', 'Government'],
        'Уровень жизни': ['生活水平', 'Standard of living'],
        обязательно: ['必填', 'required'],
        'Выберите…': ['请选择…', 'Select…'],
        'Выбрать дату': ['选择日期', 'Choose date'],
        Нет: ['否', 'No'],
        Да: ['是', 'Yes'],
        Операция: ['操作', 'Operation'],
        'Средняя высота над уровнем моря': ['平均海拔', 'Average elevation'],
        'Количество городов по площади': ['按面积统计城市数量', 'City counts by area'],
        'Города: имя содержит подстроку': ['按名称子串查找城市', 'Cities whose name contains a substring'],
        'Маршрут: максимальная → минимальная площадь': ['路线：最大面积 → 最小面积', 'Route: largest → smallest area'],
        'Маршрут: начало координат → самый новый город': [
            '路线：原点 → 最新成立城市',
            'Route: origin → most recently established city'
        ],
        Подстрока: ['子串', 'Substring'],
        'Для поиска по имени': ['用于名称搜索', 'For name search'],
        Выполнить: ['执行', 'Run'],
        'Длина маршрута — расстояние по прямой с учётом высоты над уровнем моря.': [
            '路线长度为考虑海拔的直线距离。',
            'Route length is the straight-line distance including elevation.'
        ],
        'Выберите операцию.': ['请选择操作。', 'Select an operation.'],
        'Длина маршрута': ['路线长度', 'Route length'],
        'Городов пока нет.': ['暂无城市。', 'No cities yet.'],
        'Совпадений нет.': ['没有匹配项。', 'No matches.'],
        'Нет данных': ['暂无数据', 'No data'],
        'Подключение…': ['正在连接…', 'Connecting…'],
        'Соединение активно': ['连接正常', 'Connected'],
        'Не удалось выполнить действие': ['操作失败', 'Action failed'],
        Понятно: ['知道了', 'OK'],
        'Проверьте соединение и повторите попытку.': ['请检查连接后重试。', 'Check your connection and try again.'],
        'Заполните обязательное поле.': ['请填写必填项。', 'Fill in the required field.'],
        'Проверьте формат значения.': ['请检查格式。', 'Check the value format.'],
        'Значение слишком короткое.': ['输入内容过短。', 'The value is too short.'],
        'Значение меньше допустимого.': ['数值低于允许范围。', 'The value is below the allowed minimum.'],
        'Проверьте введённое значение.': ['请检查输入内容。', 'Check the entered value.'],
        'Нет соединения с сервером. Повторите попытку.': [
            '无法连接服务器，请重试。',
            'Cannot connect to the server. Try again.'
        ],
        'Нет соединения с сервером.': ['无法连接服务器。', 'Cannot connect to the server.'],
        'Не удалось подготовить форму. Обновите страницу.': [
            '表单初始化失败，请刷新页面。',
            'Could not prepare the form. Refresh the page.'
        ],
        'Не удалось загрузить список фотографий.': ['无法加载照片来源。', 'Could not load photo credits.'],
        'Неверный логин или пароль.': ['用户名或密码错误。', 'Incorrect username or password.'],
        'Пароли не совпадают.': ['两次密码不一致。', 'Passwords do not match.'],
        'Этот логин уже занят.': ['该用户名已被使用。', 'This username is already taken.'],
        'Пароль слишком длинный: максимум 72 байта UTF-8.': [
            '密码过长：UTF-8 编码最多 72 字节。',
            'Password is too long: maximum 72 UTF-8 bytes.'
        ],
        'Регистрация завершена. Войдите с новым аккаунтом.': [
            '注册成功，请登录。',
            'Registration complete. Sign in with your new account.'
        ],
        'Аккаунт создан. Теперь войдите.': ['账号已创建，请登录。', 'Account created. Please sign in.'],
        'Сессия завершена. Войдите снова.': ['会话已结束，请重新登录。', 'Your session expired. Sign in again.'],
        'Сессия завершена': ['会话已结束', 'Session expired'],
        'Неверный ответ сервера': ['服务器响应格式错误', 'Invalid server response'],
        'Ошибка HTTP': ['HTTP 错误', 'HTTP error'],
        'Не удалось выйти. Обновите страницу.': ['退出失败，请刷新页面。', 'Could not sign out. Refresh the page.'],
        'Обновите страницу и повторите действие: сеанс проверки устарел.': [
            '验证已过期，请刷新后重试。',
            'Verification expired. Refresh the page and try again.'
        ],
        'Этот объект удалён другим пользователем.': ['该对象已被其他用户删除。', 'Another user deleted this object.'],
        'Данные в системе обновлены. Введённые значения сохранены в форме. При конфликте закройте окно и откройте объект заново.':
            [
                '系统数据已更新，表单内容仍保留。如发生冲突，请关闭窗口并重新打开对象。',
                'System data changed. Your form values are preserved. If a conflict occurs, close and reopen the object.'
            ],
        'обязательное поле': ['必填项', 'required field'],
        'введите целое число.': ['请输入整数。', 'enter an integer.'],
        'число вне диапазона': ['数值超出范围', 'number outside the range of'],
        'требуется конечное число': ['需要有限数值', 'a finite number is required'],
        'Invalid field values': ['字段值无效', 'Invalid field values', 'Некорректные значения полей'],
        'Invalid values': ['数值无效', 'Invalid values', 'Некорректные значения'],
        'Invalid JSON, date format, enum, integer range or unexpected field. Check all fields.': [
            '数据格式无效，请检查日期、枚举、整数范围及字段。',
            'Invalid data. Check dates, enums, integer ranges and fields.',
            'Некорректный формат данных. Проверьте даты, перечисления, диапазоны чисел и поля.'
        ],
        'Concurrent update detected. Close this dialog and reload the object.': [
            '对象已被其他用户修改，请关闭窗口并重新打开。',
            'Another user updated this object. Close and reopen the dialog.',
            'Объект изменён другим пользователем. Закройте окно и откройте объект заново.'
        ],
        'City not found': ['城市不存在', 'City not found', 'Город не найден'],
        'Coordinates not found': ['坐标不存在', 'Coordinates not found', 'Координаты не найдены'],
        'Human not found': ['市长不存在', 'Governor not found', 'Губернатор не найден'],
        'Object not found': ['对象不存在', 'Object not found', 'Объект не найден'],
        'must not be blank': ['不能为空', 'must not be blank', 'не должно быть пустым'],
        'must not be null': ['不能为 NULL', 'must not be null', 'не должно быть null'],
        'must be greater than 0': ['必须大于 0', 'must be greater than 0', 'должно быть больше 0'],
        'y must be finite': ['Y 必须为有限数值', 'Y must be finite', 'Y должно быть конечным числом'],
        'height must be finite': ['身高必须为有限数值', 'Height must be finite', 'Рост должен быть конечным числом'],
        'Request failed': ['请求失败', 'Request failed', 'Запрос не выполнен'],
        'Cannot delete a referenced object, or the selected related object no longer exists. Unlink it from cities first.':
            [
                '对象仍被引用，或关联对象已不存在。请先解除城市关联。',
                'Cannot delete a referenced object, or the selected related object no longer exists. Unlink it from cities first.',
                'Объект используется или связанный объект уже удалён. Сначала отвяжите его от городов.'
            ],
        'Route cannot be calculated: a selected city has no metersAboveSeaLevel.': [
            '无法计算路线：选中城市缺少海拔。',
            'Route cannot be calculated: a selected city has no elevation.',
            'Невозможно рассчитать маршрут: у выбранного города не указана высота.'
        ],
        'Database constraint rejected the values. Check positive numbers, required fields and relationships.': [
            '数据违反数据库约束，请检查正数、必填项和关联。',
            'Database constraints rejected the values. Check positive numbers, required fields and relationships.',
            'Проверьте положительные числа, обязательные поля и связи: нарушено ограничение базы данных.'
        ],
        'Numbers are too large for this calculation.': [
            '数值过大，无法计算。',
            'Numbers are too large for this calculation.',
            'Числа слишком велики для расчёта.'
        ],
        'Database operation failed. Check the server log and database connection.': [
            '数据库操作失败，请检查服务器日志和连接。',
            'Database operation failed. Check the server log and database connection.',
            'Ошибка базы данных. Проверьте журнал сервера и соединение.'
        ],
        '● Соединение активно': ['● 连接正常', '● Connected'],
        'Страница {page} / {pages} · Всего: {total}': [
            '第 {page} / {pages} 页 · 共 {total} 项',
            'Page {page} / {pages} · Total: {total}'
        ],
        'Object was changed by another user. Close this dialog and reload before editing.': [
            '对象已被其他用户修改，请关闭窗口并重新打开后编辑。',
            'Another user changed this object. Close and reopen it before editing.',
            'Объект изменён другим пользователем. Закройте окно и откройте его заново.'
        ],
        'Введите логин.': ['请输入用户名。', 'Enter a username.'],
        'Логин: 3–32 латинские буквы, цифры или _.': [
            '用户名须为 3–32 位英文字母、数字或下划线。',
            'Username: 3–32 Latin letters, digits or _.'
        ],
        'Пароль: от 8 до 72 символов.': ['密码须为 8–72 个字符。', 'Password: 8–72 characters.'],
        'Регистрация завершена. Теперь войдите.': ['注册成功，请登录。', 'Registration complete. Please sign in.'],
        'число вне диапазона long': ['数值超出 Long 范围', 'number outside the Long range'],
        'число вне диапазона int': ['数值超出 Integer 范围', 'number outside the Integer range'],
        'area must be finite': ['面积必须为有限数值', 'Area must be finite', 'Площадь должна быть конечным числом'],
        'Аккаунт создан. Теперь войдите с вашим паролем.': [
            '账号已创建，请使用你的密码登录。',
            'Account created. Sign in with your password.'
        ],
        Name: ['名称', 'Name'],
        Coordinates: ['坐标', 'Coordinates'],
        CreationDate: ['创建日期', 'Creation date'],
        Area: ['面积', 'Area'],
        Population: ['人口', 'Population'],
        EstablishmentDate: ['成立日期', 'Establishment date'],
        Capital: ['首都', 'Capital'],
        MetersAboveSeaLevel: ['海拔', 'Elevation'],
        Climate: ['气候', 'Climate'],
        Government: ['政体', 'Government'],
        StandardOfLiving: ['生活水平', 'Standard of living'],
        Governor: ['州长', 'Governor'],
        'Governor.name': ['州长姓名', 'Governor name'],
        Age: ['年龄', 'Age'],
        Height: ['身高', 'Height'],
        Birthday: ['出生日期', 'Birthday'],
        Count: ['数量', 'Count'],
        'must be greater than -531': ['必须大于 -531', 'must be greater than -531', 'должно быть больше -531'],
        'must be greater than or equal to 0': [
            '必须大于或等于 0',
            'must be greater than or equal to 0',
            'должно быть не меньше 0'
        ],
        'Unknown string column or sort field': [
            '筛选或排序字段无效',
            'Unknown filter or sort field',
            'Неизвестное поле фильтрации или сортировки'
        ],
        'page must be >= 0; size must be 1..100': [
            '页码不能为负，每页数量须为 1–100',
            'Page must be >= 0; size must be 1..100',
            'Номер страницы должен быть неотрицательным, размер — от 1 до 100'
        ]
    };
    let language = 'ru';
    try {
        language = localStorage.getItem('city-language') || 'ru';
    } catch {
        /* 不保存偏好仍可切换。 */
    }
    if (!['ru', 'zh', 'en'].includes(language)) language = 'ru';
    function t(key) {
        const text = String(key);
        const index = { zh: 0, en: 1, ru: 2 }[language];
        if (words[text]) return words[text][index] || text;
        const missing = text.match(/^(City|Human|Coordinates) #(\d+) not found$/);
        if (missing) return t(missing[1] + ' not found') + ' #' + missing[2];
        // 组合标题和逐项错误仍用同一词典，不翻译用户输入或数据库值。
        return text
            .split(/(\n| · |: )/)
            .map((part) => {
                if (words[part]) return words[part][index] || part;
                const match = part.match(/^([←＋] ?)?(.*?)( ↗| →| \*| #\d+)?$/);
                return match && words[match[2]]
                    ? (match[1] || '') + (words[match[2]][index] || match[2]) + (match[3] || '')
                    : part;
            })
            .join('');
    }
    function text(element, key) {
        element.dataset.i18n = key;
        element.textContent = t(key);
    }
    function html(key) {
        const escape = (value) =>
            String(value).replace(
                /[&<>"']/g,
                (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]
            );
        return '<span data-i18n="' + escape(key) + '">' + escape(t(key)) + '</span>';
    }
    function translate(root = document) {
        const elements = [...root.querySelectorAll('[data-i18n],[data-i18n-placeholder],[data-i18n-label]')];
        if (root.dataset?.i18n !== undefined) elements.unshift(root);
        for (const element of elements) {
            if (element.dataset.i18n !== undefined) element.textContent = t(element.dataset.i18n);
            if (element.dataset.i18nPlaceholder) element.placeholder = t(element.dataset.i18nPlaceholder);
            if (element.dataset.i18nLabel) element.setAttribute('aria-label', t(element.dataset.i18nLabel));
        }
    }
    function init() {
        const select = document.getElementById('languageSelect');
        const title = document.title;
        function apply() {
            document.documentElement.lang = language;
            document.title = t(title);
            select.value = language;
            translate();
            window.dispatchEvent(new Event('languagechange'));
        }
        select.onchange = () => {
            language = select.value;
            try {
                localStorage.setItem('city-language', language);
            } catch {
                /* 保持当前页可用。 */
            }
            apply();
        };
        apply();
    }
    return { t, text, html, translate, init };
})();
