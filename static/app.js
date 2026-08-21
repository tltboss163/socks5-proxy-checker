let currentResults = [];
let currentFilter = 'all';

// Tabs
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
    });
});

// File drag & drop
const fileDrop = document.getElementById('file-drop');
fileDrop.addEventListener('dragover', (e) => { e.preventDefault(); fileDrop.classList.add('dragover'); });
fileDrop.addEventListener('dragleave', () => fileDrop.classList.remove('dragover'));
fileDrop.addEventListener('drop', (e) => {
    e.preventDefault();
    fileDrop.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length) document.getElementById('proxy-file').files = files;
});

// Check text
const checkBtn = document.getElementById('check-btn');
checkBtn.addEventListener('click', async () => {
    const text = document.getElementById('proxy-input').value.trim();
    if (!text) { alert('Введите хотя бы один прокси'); return; }

    const lines = text.split('\n').filter(l => l.trim());
    const timeout = parseInt(document.getElementById('timeout').value) || 15;
    const downloadTest = document.getElementById('download-test').checked;

    await runCheck(lines, timeout, downloadTest);
});

// Check file
const checkFileBtn = document.getElementById('check-file-btn');
checkFileBtn.addEventListener('click', async () => {
    const file = document.getElementById('proxy-file').files[0];
    if (!file) { alert('Выберите файл'); return; }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('timeout', document.getElementById('timeout-file').value || '15');
    formData.append('download_test', document.getElementById('download-test-file').checked ? 'true' : 'false');

    showProgress('Проверяем прокси из файла...');
    try {
        const resp = await fetch('/api/check/file', { method: 'POST', body: formData });
        const data = await resp.json();
        handleResults(data);
    } catch (e) {
        alert('Ошибка: ' + e.message);
    }
    hideProgress();
});

// Parse from websites
const parseBtn = document.getElementById('parse-btn');
parseBtn.addEventListener('click', async () => {
    const timeout = parseInt(document.getElementById('timeout-parse').value) || 15;
    const downloadTest = document.getElementById('download-test-parse').checked;
    const maxProxies = parseInt(document.getElementById('max-proxies').value) || 200;

    showProgress('🌐 Парсим прокси с сайтов... Это займёт 20–40 секунд');
    try {
        const resp = await fetch('/api/parse', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ timeout, download_test: downloadTest, max_proxies: maxProxies })
        });
        if (!resp.ok) {
            const err = await resp.json();
            alert('Ошибка: ' + (err.detail || 'Неизвестная ошибка'));
            hideProgress();
            return;
        }
        const data = await resp.json();
        handleParseResults(data);
    } catch (e) {
        alert('Ошибка: ' + e.message);
    }
    hideProgress();
});

async function runCheck(proxies, timeout, downloadTest) {
    showProgress('Проверяем прокси...');
    try {
        const resp = await fetch('/api/check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ proxies, timeout, download_test: downloadTest })
        });
        const data = await resp.json();
        handleResults(data);
    } catch (e) {
        alert('Ошибка: ' + e.message);
    }
    hideProgress();
}

function showProgress(text) {
    document.getElementById('progress').style.display = 'block';
    document.getElementById('progress-text').textContent = text || 'Проверяем прокси...';
    document.getElementById('results').style.display = 'none';
}

function hideProgress() {
    document.getElementById('progress').style.display = 'none';
}

function handleResults(data) {
    currentResults = data.results || [];
    document.getElementById('stat-total').textContent = data.total;
    document.getElementById('stat-working').textContent = data.working;
    document.getElementById('stat-failed').textContent = data.failed;
    document.getElementById('results').style.display = 'block';
    renderTable();
}

function handleParseResults(data) {
    currentResults = data.results || [];
    document.getElementById('stat-total').textContent = data.checked_count;
    document.getElementById('stat-working').textContent = data.working;
    document.getElementById('stat-failed').textContent = data.failed;
    document.getElementById('results').style.display = 'block';
    renderTable();
    alert(`Спарсено: ${data.parsed_count}\nПроверено: ${data.checked_count}\nРабочих: ${data.working}`);
}

function renderTable() {
    const tbody = document.getElementById('results-body');
    tbody.innerHTML = '';

    const countryFilter = document.getElementById('country-filter').value.toLowerCase();

    const filtered = currentResults.filter(r => {
        if (currentFilter === 'working' && !r.is_working) return false;
        if (currentFilter === 'dead' && r.is_working) return false;
        if (countryFilter && (!r.country || !r.country.toLowerCase().includes(countryFilter))) return false;
        return true;
    });

    filtered.forEach(r => {
        const tr = document.createElement('tr');
        const statusClass = r.is_working ? 'working' : 'dead';
        const statusText = r.is_working ? 'OK' : 'FAIL';

        const latencyClass = r.latency_ms < 500 ? 'latency-good' : r.latency_ms < 2000 ? 'latency-mid' : 'latency-bad';
        const speedClass = r.download_speed_kbps > 500 ? 'speed-good' : r.download_speed_kbps > 100 ? 'speed-mid' : 'speed-bad';

        const flag = r.country_code ? getFlagEmoji(r.country_code) : '🏳️';
        const authBadge = r.username ? '<span class="auth-badge">auth</span>' : '';

        tr.innerHTML = `
            <td><span class="status-dot ${statusClass}"></span>${statusText}</td>
            <td class="proxy-cell">${r.host}:${r.port}${authBadge}</td>
            <td><span class="flag">${flag}</span>${r.country || '—'}</td>
            <td class="${latencyClass}">${r.latency_ms} ms</td>
            <td class="${speedClass}">${r.download_speed_kbps} KB/s</td>
            <td>${r.download_time_ms} ms</td>
            <td class="error-text" title="${r.error || ''}">${r.error || '—'}</td>
        `;
        tbody.appendChild(tr);
    });
}

function getFlagEmoji(code) {
    return code.toUpperCase().replace(/./g, ch => String.fromCodePoint(127397 + ch.charCodeAt(0)));
}

// Filters
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentFilter = btn.dataset.filter;
        renderTable();
    });
});

document.getElementById('country-filter').addEventListener('input', renderTable);

// Export
function download(filename, content, type) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

document.getElementById('export-json').addEventListener('click', () => {
    download('proxies.json', JSON.stringify(currentResults, null, 2), 'application/json');
});

document.getElementById('export-txt').addEventListener('click', () => {
    const lines = currentResults
        .filter(r => r.is_working)
        .map(r => {
            const auth = r.username ? `${r.username}:${r.password}@` : '';
            return `${auth}${r.host}:${r.port}`;
        });
    download('proxies.txt', lines.join('\n'), 'text/plain');
});

document.getElementById('export-csv').addEventListener('click', () => {
    const header = 'host,port,country,country_code,latency_ms,download_speed_kbps,is_working,error\n';
    const rows = currentResults.map(r => 
        `${r.host},${r.port},${r.country || ''},${r.country_code || ''},${r.latency_ms},${r.download_speed_kbps},${r.is_working},"${(r.error || '').replace(/"/g, '""')}"`
    );
    download('proxies.csv', header + rows.join('\n'), 'text/csv');
});
