'use strict';
window.UI = {
    // 所有页面共用自定义错误弹窗；使用 textContent，避免把错误内容当作 HTML。
    error(message) {
        let dialog = document.getElementById('errorDialog');
        if (!dialog) {
            dialog = document.createElement('dialog');
            dialog.id = 'errorDialog';
            dialog.className = 'error-dialog';
            dialog.setAttribute('aria-labelledby', 'errorTitle');
            dialog.setAttribute('aria-describedby', 'errorMessage');
            dialog.innerHTML =
                '<div class="error-symbol">!</div><h2 id="errorTitle" data-i18n="Не удалось выполнить действие">Не удалось выполнить действие</h2><p id="errorMessage"></p><button type="button" data-i18n="Понятно" autofocus>Понятно</button>';
            document.body.append(dialog);
            dialog.querySelector('button').onclick = () => dialog.close();
        }
        I18n.text(document.getElementById('errorMessage'), message || 'Проверьте соединение и повторите попытку.');
        I18n.translate(dialog);
        if (!dialog.open) dialog.showModal();
    },
    validate(form) {
        // 表单设置 novalidate 后，由这里汇总错误，不再弹出浏览器默认校验气泡。
        const errors = [];
        form.querySelectorAll('input,select,textarea').forEach((input) => {
            input.removeAttribute('aria-invalid');
            if (!input.checkValidity()) {
                input.setAttribute('aria-invalid', 'true');
                const label = input.getAttribute('aria-label') || input.name;
                // 按浏览器校验状态选择说明，避免多层嵌套条件，保持原有错误提示。
                const messages = {
                    valueMissing: 'Заполните обязательное поле.',
                    patternMismatch: 'Проверьте формат значения.',
                    tooShort: 'Значение слишком короткое.',
                    rangeUnderflow: 'Значение меньше допустимого.'
                };
                const reason = Object.keys(messages).find((key) => input.validity[key]);
                errors.push(label + ': ' + (messages[reason] || 'Проверьте введённое значение.'));
            }
        });
        if (errors.length) {
            this.error(errors.join('\n'));
            return false;
        }
        return true;
    }
};

I18n.init();
