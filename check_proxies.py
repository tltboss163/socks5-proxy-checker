#!/usr/bin/env python3
"""Standalone checker for GitHub Actions — парсит и проверяет SOCKS5 прокси."""

import asyncio
import json
import re
import os
from datetime import datetime
from typing import List, Optional, Dict, Set

import aiohttp
import aiohttp_socks
import httpx

RESULT_JSON = "working_proxies.json"
RESULT_TXT = "working_proxies.txt"
RESULT_CSV = "working_proxies.csv"
README = "README.md"

DOWNLOAD_URL = "https://speed.hetzner.de/1MB.bin"
DOWNLOAD_SIZE = 1048576
TIMEOUT = 15
CONCURRENT = 50

SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt",
    "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks5.txt",
    "https://raw.githubusercontent.com/saschazesiger/server-proxies/master/socks5.txt",
    "https://api.proxyscrape.com/v2/?request=get&protocol=socks5&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://www.proxy-list.download/api/v1/get?type=socks5",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

PROXY_RE = re.compile(r"(?:\d{1,3}\.){3}\d{1,3}:\d{2,5}")


async def fetch_source(session: aiohttp.ClientSession, url: str) -> str:
    try:
        async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status == 200:
                return await resp.text()
    except Exception:
        pass
    return ""


async def fetch_all_proxies() -> List[str]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_source(session, url) for url in SOURCES]
        texts = await asyncio.gather(*tasks)

    proxies: Set[str] = set()
    for text in texts:
        for match in PROXY_RE.finditer(text):
            proxies.add(match.group())

    return sorted(proxies)


def parse_proxy(line: str) -> Optional[Dict]:
    line = line.strip()
    if not line:
        return None
    parts = line.split(":")
    if len(parts) == 2:
        try:
            port = int(parts[1])
            return {"host": parts[0], "port": port, "url": f"socks5://{parts[0]}:{port}"}
        except ValueError:
            pass
    return None


async def get_country(ip: str) -> Dict[str, Optional[str]]:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"http://ip-api.com/json/{ip}?fields=status,country,countryCode")
            data = resp.json()
            if data.get("status") == "success":
                return {"country": data.get("country"), "country_code": data.get("countryCode")}
    except Exception:
        pass
    return {"country": None, "country_code": None}


async def check_one(proxy: Dict, semaphore: asyncio.Semaphore) -> Dict:
    async with semaphore:
        connector = aiohttp_socks.ProxyConnector.from_url(proxy["url"])
        session_timeout = aiohttp.ClientTimeout(total=TIMEOUT)
        start = time.monotonic()
        latency = None
        download_speed = 0.0
        download_time = 0.0
        error = None
        is_working = False
        country = None
        country_code = None

        try:
            async with aiohttp.ClientSession(connector=connector, timeout=session_timeout) as session:
                async with session.get("http://httpbin.org/ip") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        real_ip = data.get("origin", proxy["host"]).split(",")[0].strip()
                        latency = round((time.monotonic() - start) * 1000, 2)
                        is_working = True
                        geo = await get_country(real_ip)
                        country = geo["country"]
                        country_code = geo["country_code"]
                    else:
                        error = f"HTTP {resp.status}"

                if is_working:
                    dl_start = time.monotonic()
                    try:
                        async with session.get(DOWNLOAD_URL) as dl_resp:
                            if dl_resp.status == 200:
                                total = 0
                                async for chunk in dl_resp.content.iter_chunked(8192):
                                    total += len(chunk)
                                    if total >= DOWNLOAD_SIZE:
                                        break
                                dl_time = time.monotonic() - dl_start
                                download_time = round(dl_time * 1000, 2)
                                download_speed = round((total / 1024) / max(dl_time, 0.001), 2)
                            else:
                                error = f"DL HTTP {dl_resp.status}"
                    except Exception as e:
                        error = f"DL: {str(e)[:80]}"

        except asyncio.TimeoutError:
            error = "Timeout"
        except Exception as e:
            error = str(e)[:120]
        finally:
            connector.close()

        return {
            **proxy,
            "country": country,
            "country_code": country_code,
            "latency_ms": latency or round((time.monotonic() - start) * 1000, 2),
            "download_speed_kbps": download_speed,
            "download_time_ms": download_time,
            "is_working": is_working,
            "error": error,
            "checked_at": datetime.utcnow().isoformat() + "Z"
        }


async def main():
    print("🌐 Парсим прокси с сайтов...")
    proxies_lines = await fetch_all_proxies()
    print(f"Спарсено: {len(proxies_lines)}")

    if not proxies_lines:
        print("Не удалось спарсить прокси!")
        return

    proxies = [p for p in (parse_proxy(line) for line in proxies_lines) if p]
    print(f"Для проверки: {len(proxies)}")

    semaphore = asyncio.Semaphore(CONCURRENT)
    tasks = [check_one(p, semaphore) for p in proxies]
    results = await asyncio.gather(*tasks)
    results.sort(key=lambda x: (not x["is_working"], x["latency_ms"]))

    working = [r for r in results if r["is_working"]]

    # JSON
    with open(RESULT_JSON, "w", encoding="utf-8") as f:
        json.dump({
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "parsed_count": len(proxies_lines),
            "total_checked": len(proxies),
            "working_count": len(working),
            "proxies": results
        }, f, indent=2, ensure_ascii=False)

    # TXT
    with open(RESULT_TXT, "w", encoding="utf-8") as f:
        for r in working:
            flag = get_flag(r.get('country_code')) if r.get('country_code') else '🏳️'
            f.write(f"{r['host']}:{r['port']}  # {flag} {r.get('country','?')} | {r['latency_ms']}ms | {r['download_speed_kbps']}KB/s\n")

    # CSV
    with open(RESULT_CSV, "w", encoding="utf-8") as f:
        f.write("host,port,country,country_code,latency_ms,download_speed_kbps,download_time_ms,is_working,error\n")
        for r in results:
            error_escaped = str(r.get("error", "")).replace('"', '""')
            f.write(f"{r['host']},{r['port']},{r.get('country','')},{r.get('country_code','')},"
                    f"{r['latency_ms']},{r['download_speed_kbps']},{r['download_time_ms']},"
                    f"{r['is_working']},\"{error_escaped}\"\n")

    # README
    rows = ""
    for r in results:
        flag = get_flag(r.get('country_code')) if r.get('country_code') else '🏳️'
        status = "✅" if r["is_working"] else "❌"
        speed = f"{r['download_speed_kbps']} KB/s" if r['is_working'] else "—"
        rows += f"| {status} | `{r['host']}:{r['port']}` | {flag} {r.get('country','?')} | {r['latency_ms']}ms | {speed} | {r.get('error','—')} |\n"

    readme = f"""# 🧦 SOCKS5 Proxy Checker

![Workflow](https://github.com/{os.getenv('GITHUB_REPOSITORY','user/repo')}/actions/workflows/check-proxies.yml/badge.svg)

**Последняя проверка:** `{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}`

| Статус | Прокси | Страна | Задержка | Скорость | Ошибка |
|--------|--------|--------|----------|----------|--------|
{rows}

**Спарсено:** {len(proxies_lines)} | **Проверено:** {len(proxies)} | **Рабочих:** {len(working)}

---

## 📥 Файлы

- `working_proxies.json` — полные данные в JSON
- `working_proxies.txt` — список рабочих прокси
- `working_proxies.csv` — таблица для Excel/Google Sheets

## 🌐 Источники

Прокси спарсены автоматически с:
- GitHub репозиториев proxy-листов
- ProxyScrape API
- Proxy-List.download

Workflow запускается автоматически каждые 6 часов.
"""

    with open(README, "w", encoding="utf-8") as f:
        f.write(readme)

    print(f"✅ Готово! Спарсено: {len(proxies_lines)} | Проверено: {len(proxies)} | Рабочих: {len(working)}")


def get_flag(code: str) -> str:
    return "".join(chr(ord(c) + 127397) for c in code.upper())


if __name__ == "__main__":
    import time
    asyncio.run(main())
