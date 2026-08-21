import asyncio
import time
import re
from typing import List, Optional, Dict
from dataclasses import dataclass

import aiohttp
import aiohttp_socks

from app.models import ProxyResult

MAX_CONCURRENT = int(__import__("os").getenv("MAX_CONCURRENT", "300"))
# Один запрос через прокси отдаёт и пинг, и страну exit-IP
GEO_URL = __import__("os").getenv(
    "GEO_URL",
    "http://ip-api.com/json/?fields=status,message,country,countryCode"
)
DOWNLOAD_TEST_URL = __import__("os").getenv(
    "DOWNLOAD_TEST_URL",
    "http://speedtest.tele2.net/1MB.zip"
)
DOWNLOAD_SIZE = int(__import__("os").getenv("DOWNLOAD_SIZE_BYTES", "1048576"))
PROXY_TIMEOUT = int(__import__("os").getenv("PROXY_TIMEOUT", "10"))


@dataclass
class ParsedProxy:
    host: str
    port: int
    username: Optional[str]
    password: Optional[str]
    url: str


def parse_proxy(line: str) -> Optional[ParsedProxy]:
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    m = re.match(
        r"^(?P<user>[^:]+):(?P<pass>[^@]+)@(?P<host>[^:]+):(?P<port>\d+)$",
        line
    )
    if m:
        return ParsedProxy(
            host=m.group("host"),
            port=int(m.group("port")),
            username=m.group("user"),
            password=m.group("pass"),
            url=f"socks5://{m.group('user')}:{m.group('pass')}@{m.group('host')}:{m.group('port')}"
        )

    parts = line.split(":")
    if len(parts) == 4:
        return ParsedProxy(
            host=parts[0],
            port=int(parts[1]),
            username=parts[2],
            password=parts[3],
            url=f"socks5://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
        )

    if len(parts) == 2:
        try:
            port = int(parts[1])
            return ParsedProxy(
                host=parts[0],
                port=port,
                username=None,
                password=None,
                url=f"socks5://{parts[0]}:{port}"
            )
        except ValueError:
            pass

    return None


async def check_proxy(
    proxy: ParsedProxy,
    semaphore: asyncio.Semaphore,
    timeout: int = PROXY_TIMEOUT,
    do_download: bool = True
) -> ProxyResult:
    async with semaphore:
        connector = aiohttp_socks.ProxyConnector.from_url(proxy.url)
        session_timeout = aiohttp.ClientTimeout(total=timeout)
        start = time.monotonic()
        latency = None
        download_speed = 0.0
        download_time = 0.0
        error = None
        is_working = False
        country = None
        country_code = None

        try:
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=session_timeout
            ) as session:
                async with session.get(GEO_URL) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        latency = round((time.monotonic() - start) * 1000, 2)
                        is_working = True
                        if data.get("status") == "success":
                            country = data.get("country")
                            country_code = data.get("countryCode")
                    else:
                        error = f"HTTP {resp.status}"

                if is_working and do_download:
                    dl_start = time.monotonic()
                    try:
                        async with session.get(DOWNLOAD_TEST_URL) as dl_resp:
                            if dl_resp.status == 200:
                                total_bytes = 0
                                async for chunk in dl_resp.content.iter_chunked(8192):
                                    total_bytes += len(chunk)
                                    if total_bytes >= DOWNLOAD_SIZE:
                                        break
                                dl_time = time.monotonic() - dl_start
                                download_time = round(dl_time * 1000, 2)
                                download_speed = round(
                                    (total_bytes / 1024) / max(dl_time, 0.001), 2
                                )
                            else:
                                error = f"Download HTTP {dl_resp.status}"
                    except Exception as e:
                        error = f"Download error: {str(e)[:80]}"

        except asyncio.TimeoutError:
            error = "Timeout"
        except Exception as e:
            error = str(e)[:120]
        finally:
            await connector.close()

        return ProxyResult(
            host=proxy.host,
            port=proxy.port,
            username=proxy.username,
            password=proxy.password,
            url=proxy.url,
            country=country,
            country_code=country_code,
            latency_ms=latency or round((time.monotonic() - start) * 1000, 2),
            download_speed_kbps=download_speed,
            download_time_ms=download_time,
            is_working=is_working,
            error=error,
            checked_at=__import__("datetime").datetime.utcnow()
        )


async def check_proxies(
    proxy_lines: List[str],
    timeout: int = PROXY_TIMEOUT,
    do_download: bool = True
) -> List[ProxyResult]:
    proxies = [p for p in (parse_proxy(line) for line in proxy_lines) if p]
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    tasks = [
        check_proxy(p, semaphore, timeout, do_download)
        for p in proxies
    ]
    results = await asyncio.gather(*tasks)
    return sorted(results, key=lambda x: (not x.is_working, x.latency_ms))
