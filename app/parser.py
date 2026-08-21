"""Парсинг бесплатных SOCKS5 прокси с публичных источников."""

import asyncio
import re
from typing import List, Set

import aiohttp


SOURCES = [
    # Прямые текстовые списки host:port
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt",
    "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks5.txt",
    "https://raw.githubusercontent.com/saschazesiger/server-proxies/master/socks5.txt",
    # API
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
                text = await resp.text()
                return text
    except Exception:
        pass
    return ""


async def fetch_all_proxies() -> List[str]:
    """Парсит прокси со всех источников и возвращает уникальный список host:port."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_source(session, url) for url in SOURCES]
        texts = await asyncio.gather(*tasks)

    proxies: Set[str] = set()
    for text in texts:
        for match in PROXY_RE.finditer(text):
            proxies.add(match.group())

    return sorted(proxies)


def parse_proxies_from_text(text: str) -> List[str]:
    """Извлекает host:port из произвольного текста."""
    return sorted(set(PROXY_RE.findall(text)))
