'use strict';
const byId = id => document.getElementById(id);
const input = byId('input');
const preview = byId('preview');

function resetDOM() {
    preview.replaceChildren();
    byId('flag').textContent = 'TAYYOR';
}

byId('weak').addEventListener('click', () => {
    resetDOM();
    preview.textContent = input.value; // Deliberately unsafe lab sink.
});

byId('safe').addEventListener('click', () => {
    resetDOM();
    preview.textContent = input.value;
});

byId('reset').addEventListener('click', resetDOM);

async function loadAPI() {
    const button = byId('fetch');
    button.disabled = true;
    byId('api').textContent = '';
    byId('status').textContent = 'Yuklanmoqda...';
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 3000);

    try {
        const params = new URLSearchParams({q: input.value});
        const response = await fetch('/api/echo?' + params, {
            signal: controller.signal, credentials: 'omit', cache: 'no-store'
        });
        if (!response.ok) throw new Error('HTTP ' + response.status);

        const kind = (response.headers.get('Content-Type') || '')
            .split(';')[0].trim().toLowerCase();
        if (kind !== 'application/json') {
            throw new Error('JSON javob kutilgan edi.');
        }

        const data = await response.json();
        if (!data || typeof data.text !== 'string') {
            throw new Error("Javob tuzilmasi noto‘g‘ri.");
        }

        byId('api').textContent = data.text;
        byId('status').textContent = 'Muvaffaqiyat: HTTP 200';
    } catch (error) {
        const message = error.name === 'AbortError'
            ? 'Kutish vaqti tugadi.' : error.message;
        byId('status').textContent = 'Xato: ' + message;
    } finally {
        clearTimeout(timer);
        button.disabled = false;
    }
}

byId('fetch').addEventListener('click', loadAPI);