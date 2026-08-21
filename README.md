# ЁЯзж SOCKS5 Proxy Checker

╨Я╨╛╨╗╨╜╨╛╤Ж╨╡╨╜╨╜╤Л╨╣ ╤Б╨╡╤А╨▓╨╕╤Б ╨┤╨╗╤П ╨┐╤А╨╛╨▓╨╡╤А╨║╨╕ SOCKS5 ╨┐╤А╨╛╨║╤Б╨╕: **╨┐╨░╤А╤Б╨╕╨╜╨│ ╤Б ╤Б╨░╨╣╤В╨╛╨▓**, ╨╛╨┐╤А╨╡╨┤╨╡╨╗╨╡╨╜╨╕╨╡ ╤Б╤В╤А╨░╨╜╤Л, ╨╖╨░╨┤╨╡╤А╨╢╨║╨░ ╨╕ ╤Б╨║╨╛╤А╨╛╤Б╤В╤М ╤Б╨║╨░╤З╨╕╨▓╨░╨╜╨╕╤П.

---

## тЬи ╨Т╨╛╨╖╨╝╨╛╨╢╨╜╨╛╤Б╤В╨╕

| ╨д╤Г╨╜╨║╤Ж╨╕╤П | ╨Ю╨┐╨╕╤Б╨░╨╜╨╕╨╡ |
|---------|----------|
| ЁЯМР **╨Я╨░╤А╤Б╨╕╨╜╨│** | ╨Р╨▓╤В╨╛╨╝╨░╤В╨╕╤З╨╡╤Б╨║╨╕ ╤Б╨╛╨▒╨╕╤А╨░╨╡╤В SOCKS5 ╤Б 10+ ╨┐╤Г╨▒╨╗╨╕╤З╨╜╤Л╤Е ╨╕╤Б╤В╨╛╤З╨╜╨╕╨║╨╛╨▓ |
| ЁЯМН **╨б╤В╤А╨░╨╜╨░** | ╨Ю╨┐╤А╨╡╨┤╨╡╨╗╤П╨╡╤В ╤Б╤В╤А╨░╨╜╤Г ╨┐╨╛ IP ╤З╨╡╤А╨╡╨╖ `ip-api.com` |
| тЪб **╨Ч╨░╨┤╨╡╤А╨╢╨║╨░** | ╨в╨╛╤З╨╜╤Л╨╣ ╨╖╨░╨╝╨╡╤А latency |
| ЁЯУе **╨б╨║╨╛╤А╨╛╤Б╤В╤М** | ╨Р╤Б╨╕╨╜╤Е╤А╨╛╨╜╨╜╨░╤П ╨╖╨░╨│╤А╤Г╨╖╨║╨░ 1 ╨Ь╨С ╨┤╨╗╤П ╨╖╨░╨╝╨╡╤А╨░ ╤А╨╡╨░╨╗╤М╨╜╨╛╨╣ ╤Б╨║╨╛╤А╨╛╤Б╤В╨╕ |
| ЁЯЦея╕П **╨Т╨╡╨▒-╨╕╨╜╤В╨╡╤А╤Д╨╡╨╣╤Б** | ╨Ъ╤А╨░╤Б╨╕╨▓╤Л╨╣ UI ╤Б ╤Д╨╕╨╗╤М╤В╤А╨░╨╝╨╕ ╨╕ ╤Н╨║╤Б╨┐╨╛╤А╤В╨╛╨╝ |
| ЁЯФМ **REST API** | ╨Я╨╛╨╗╨╜╤Л╨╣ API ╨┤╨╗╤П ╨╕╨╜╤В╨╡╨│╤А╨░╤Ж╨╕╨╕ |
| ЁЯдЦ **GitHub Actions** | ╨Р╨▓╤В╨╛╨┐╤А╨╛╨▓╨╡╤А╨║╨░ ╨║╨░╨╢╨┤╤Л╨╡ 6 ╤З╨░╤Б╨╛╨▓ |

---

## ЁЯЪА ╨С╤Л╤Б╤В╤А╤Л╨╣ ╤Б╤В╨░╤А╤В

### Docker

```bash
git clone <repo>
cd socks5-proxy-checker
docker-compose up -d
```

╨Ю╤В╨║╤А╨╛╨╣ `http://localhost:8000`

### ╨С╨╡╨╖ Docker

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## ЁЯУб REST API

### POST `/api/parse` тнР
╨б╨┐╨░╤А╤Б╨╕╤В╤М ╨┐╤А╨╛╨║╤Б╨╕ ╤Б ╤Б╨░╨╣╤В╨╛╨▓ ╨╕ ╤Б╤А╨░╨╖╤Г ╨┐╤А╨╛╨▓╨╡╤А╨╕╤В╤М.

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
╨Я╤А╨╛╨▓╨╡╤А╨╕╤В╤М ╤Б╨▓╨╛╨╣ ╤Б╨┐╨╕╤Б╨╛╨║ ╨┐╤А╨╛╨║╤Б╨╕.

```bash
curl -X POST http://localhost:8000/api/check \
  -H "Content-Type: application/json" \
  -d '{"proxies": ["127.0.0.1:1080"], "timeout": 15, "download_test": true}'
```

### GET `/api/results`
╨Я╨╛╤Б╨╗╨╡╨┤╨╜╨╕╨╡ ╤А╨╡╨╖╤Г╨╗╤М╤В╨░╤В╤Л.

### GET `/api/results/working`
╨в╨╛╨╗╤М╨║╨╛ ╤А╨░╨▒╨╛╤З╨╕╨╡.

---

## ЁЯМР ╨Ш╤Б╤В╨╛╤З╨╜╨╕╨║╨╕ ╨┐╨░╤А╤Б╨╕╨╜╨│╨░

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

## тЪЩя╕П ╨Я╨╡╤А╨╡╨╝╨╡╨╜╨╜╤Л╨╡ ╨╛╨║╤А╤Г╨╢╨╡╨╜╨╕╤П

| ╨Я╨╡╤А╨╡╨╝╨╡╨╜╨╜╨░╤П | ╨Я╨╛ ╤Г╨╝╨╛╨╗╤З╨░╨╜╨╕╤О | ╨Ю╨┐╨╕╤Б╨░╨╜╨╕╨╡ |
|------------|-------------|----------|
| `MAX_CONCURRENT` | 50 | ╨Ю╨┤╨╜╨╛╨▓╤А╨╡╨╝╨╡╨╜╨╜╤Л╤Е ╨┐╤А╨╛╨▓╨╡╤А╨╛╨║ |
| `DOWNLOAD_TEST_URL` | speed.hetzner.de/1MB.bin | URL ╨┤╨╗╤П ╤В╨╡╤Б╤В╨░ ╤Б╨║╨╛╤А╨╛╤Б╤В╨╕ |
| `DOWNLOAD_SIZE_BYTES` | 1048576 | ╨а╨░╨╖╨╝╨╡╤А ╨╖╨░╨│╤А╤Г╨╖╨║╨╕ |
| `PROXY_TIMEOUT` | 15 | ╨в╨░╨╣╨╝╨░╤Г╤В (╤Б╨╡╨║) |

---

## ЁЯдЦ GitHub Actions

Workflow ╨╖╨░╨┐╤Г╤Б╨║╨░╨╡╤В╤Б╤П:
- **╨Р╨▓╤В╨╛╨╝╨░╤В╨╕╤З╨╡╤Б╨║╨╕** тАФ ╨║╨░╨╢╨┤╤Л╨╡ 6 ╤З╨░╤Б╨╛╨▓
- **╨Т╤А╤Г╤З╨╜╤Г╤О** тАФ ╤З╨╡╤А╨╡╨╖ ╨▓╨║╨╗╨░╨┤╨║╤Г Actions

╨а╨╡╨╖╤Г╨╗╤М╤В╨░╤В╤Л ╨║╨╛╨╝╨╝╨╕╤В╤П╤В╤Б╤П:
- `working_proxies.json`
- `working_proxies.txt`
- `working_proxies.csv`

---

## ЁЯУБ ╨б╤В╤А╤Г╨║╤В╤Г╤А╨░

```
.
тФЬтФАтФА app/
тФВ   тФЬтФАтФА main.py          # FastAPI
тФВ   тФЬтФАтФА models.py        # Pydantic
тФВ   тФЬтФАтФА checker.py       # ╨Я╤А╨╛╨▓╨╡╤А╨║╨░ ╨┐╤А╨╛╨║╤Б╨╕
тФВ   тФФтФАтФА parser.py        # ╨Я╨░╤А╤Б╨╕╨╜╨│ ╤Б ╤Б╨░╨╣╤В╨╛╨▓ тнР
тФЬтФАтФА static/              # CSS + JS
тФЬтФАтФА templates/           # HTML
тФЬтФАтФА .github/workflows/   # CI/CD
тФЬтФАтФА check_proxies.py     # Standalone ╨┤╨╗╤П Actions
тФЬтФАтФА requirements.txt
тФЬтФАтФА Dockerfile
тФФтФАтФА docker-compose.yml
```

---

## ЁЯЫбя╕П ╨Ы╨╕╤Ж╨╡╨╜╨╖╨╕╤П

MIT
