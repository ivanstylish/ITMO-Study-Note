'use strict';
const byId = (id) => document.getElementById(id);
let registering = false,
    csrf;
async function getCsrf() {
    // 登录与注册前取得当前会话的 CSRF 令牌，保持 Spring Security 的请求校验。
    const response = await fetch('/auth/csrf');
    if (!response.ok) throw Error('Не удалось подготовить форму. Обновите страницу.');
    csrf = await response.json();
}
function setMode(value) {
    registering = value;
    I18n.text(byId('authError'), '');
    byId('authSuccess').hidden = true;
    ['loginTab', 'registerTab'].forEach((id, index) => {
        const active = Boolean(index) === value;
        byId(id).classList.toggle('active', active);
        byId(id).setAttribute('aria-selected', String(active));
    });
    byId('confirmLabel').hidden = !value;
    byId('confirmation').disabled = !value;
    byId('confirmation').required = value;
    byId('passwordHint').hidden = !value;
    byId('password').autocomplete = value ? 'new-password' : 'current-password';
    if (value) {
        byId('username').pattern = '[A-Za-z0-9_]{3,32}';
        byId('password').minLength = 8;
        byId('password').maxLength = 72;
    } else {
        byId('username').removeAttribute('pattern');
        byId('password').removeAttribute('minlength');
        byId('password').removeAttribute('maxlength');
    }
    I18n.text(byId('authSubmit').firstElementChild, value ? 'Создать аккаунт' : 'Войти');
    I18n.text(byId('formTitle'), value ? 'Регистрация' : 'Вход');
    I18n.translate(document.querySelector('.auth-panel'));
}
byId('loginTab').onclick = () => setMode(false);
byId('registerTab').onclick = () => setMode(true);
byId('togglePassword').onclick = () => {
    const visible = byId('password').type === 'password';
    byId('password').type = visible ? 'text' : 'password';
    byId('togglePassword').dataset.i18nLabel = visible ? 'Скрыть пароль' : 'Показать пароль';
    I18n.translate(document.querySelector('.auth-panel'));
};
byId('authForm').onsubmit = async (event) => {
    // 注册成功后回到登录模式；只有数据库中已注册的账号才能通过认证。
    event.preventDefault();
    if (!UI.validate(event.target)) return;
    I18n.text(byId('authError'), '');
    byId('authSubmit').disabled = true;
    try {
        await getCsrf();
        const values = Object.fromEntries(new FormData(event.target));
        if (registering && values.password !== values.confirmation) throw Error('Пароли не совпадают.');
        const response = await fetch(registering ? '/auth/register' : '/login', {
            method: 'POST',
            headers: {
                [csrf.header]: csrf.token,
                'Content-Type': registering ? 'application/json' : 'application/x-www-form-urlencoded'
            },
            body: registering
                ? JSON.stringify(values)
                : new URLSearchParams({ username: values.username, password: values.password })
        });
        const result = await response.json();
        if (!response.ok) throw Error([result.message, ...Object.values(result.fields || {})].join('\n'));
        if (registering) {
            setMode(false);
            byId('password').value = '';
            byId('confirmation').value = '';
            I18n.text(byId('authSuccess'), result.message);
            byId('authSuccess').hidden = false;
            byId('password').focus();
        } else location.assign('/');
    } catch (e) {
        const message = e instanceof TypeError ? 'Нет соединения с сервером. Повторите попытку.' : e.message;
        I18n.text(byId('authError'), message);
        UI.error(message);
    } finally {
        byId('authSubmit').disabled = false;
        I18n.translate(document.querySelector('.auth-panel'));
    }
};
byId('photoCredits').onclick = async () => {
    try {
        const response = await fetch('/images/cities/credits.json');
        if (!response.ok) throw Error('Не удалось загрузить список фотографий.');
        const entries = await response.json();
        byId('creditsList').replaceChildren();
        for (const entry of entries) {
            const p = document.createElement('p');
            p.textContent = entry.city + ' — ' + entry.author + ' · ';
            const license = document.createElement('a');
            licensI18n.text(e, entry.license);
            license.href = entry.licenseUrl || entry.source;
            license.target = '_blank';
            license.rel = 'noopener noreferrer';
            const source = document.createElement('a');
            sourcI18n.text(e, ' · Оригинал ↗');
            source.href = entry.source;
            source.target = '_blank';
            source.rel = 'noopener noreferrer';
            p.append(license, source);
            byId('creditsList').append(p);
        }
        I18n.translate(byId('creditsDialog'));
        byId('creditsDialog').showModal();
    } catch (e) {
        UI.error(e.message);
    }
};
byId('closeCredits').onclick = () => byId('creditsDialog').close();
