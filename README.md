# 🧦 SOCKS5 Proxy Checker

Полноценный сервис для проверки SOCKS5 прокси: **парсинг с сайтов**, определение страны, задержка и скорость скачивания.

---

## ✨ Возможности

| Функция | Описание |
|---------|----------|
| 🌐 **Парсинг** | Автоматически собирает SOCKS5 с 10+ публичных источников |
| 🌍 **Страна** | Определяет страну по IP через `ip-api.com` |
| ⚡ **Задержка** | Точный замер latency |
| 📥 **Скорость** | Асинхронная загрузка 1 МБ для замера реальной скорости |
| 🖥️ **Веб-интерфейс** | Красивый UI с фильтрами и экспортом |
| 🔌 **REST API** | Полный API для интеграции |
| 🤖 **GitHub Actions** | Автопроверка каждые 6 часов |

---

## 🚀 Быстрый старт

### Docker

```bash
git clone <repo>
cd socks5-proxy-checker
docker-compose up -d
```

Открой `http://localhost:8000`

### Без Docker

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 📡 REST API

### POST `/api/parse` ⭐
Спарсить прокси с сайтов и сразу проверить.

```bash
curl -X POST http://localhost:8000/api/parse \
  -H "Content-Type: application/json" \
  -d '{
    "timeout": 15,
    "download_test": true,
    "max_proxies": 200
  }'
```

### POST `/api/check`
Проверить свой список прокси.

```bash
curl -X POST http://localhost:8000/api/check \
  -H "Content-Type: application/json" \
  -d '{"proxies": ["127.0.0.1:1080"], "timeout": 15, "download_test": true}'
```

### GET `/api/results`
Последние результаты.

### GET `/api/results/working`
Только рабочие.

---

## 🌐 Источники парсинга

- `TheSpeedX/PROXY-List`
- `hookzof/socks5_list`
- `ShiftyTR/Proxy-List`
- `monosans/proxy-list`
- `roosterkid/openproxylist`
- `rdavydov/proxy-list`
- `zevtyardt/proxy-list`
- `saschazesiger/server-proxies`
- `proxyscrape.com`
- `proxy-list.download`

---

## ⚙️ Переменные окружения

| Переменная | По умолчанию | Описание |
|------------|-------------|----------|
| `MAX_CONCURRENT` | 50 | Одновременных проверок |
| `DOWNLOAD_TEST_URL` | speed.hetzner.de/1MB.bin | URL для теста скорости |
| `DOWNLOAD_SIZE_BYTES` | 1048576 | Размер загрузки |
| `PROXY_TIMEOUT` | 15 | Таймаут (сек) |

---

## 🤖 GitHub Actions

Workflow запускается:
- **Автоматически** — каждые 6 часов
- **Вручную** — через вкладку Actions

Результаты коммитятся:
- `working_proxies.json`
- `working_proxies.txt`
- `working_proxies.csv`

---

## 📁 Структура

```
.
├── app/
│   ├── main.py          # FastAPI
│   ├── models.py        # Pydantic
│   ├── checker.py       # Проверка прокси
│   └── parser.py        # Парсинг с сайтов ⭐
├── static/              # CSS + JS
├── templates/           # HTML
├── .github/workflows/   # CI/CD
├── check_proxies.py     # Standalone для Actions
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## 🛡️ Лицензия

MIT
