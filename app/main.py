import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.models import CheckRequest, CheckResponse, ProxyResult, ParseRequest, ParseResponse
from app.checker import check_proxies, parse_proxy
from app.parser import fetch_all_proxies, parse_proxies_from_text

app = FastAPI(
    title="SOCKS5 Proxy Checker",
    description="Проверка SOCKS5 прокси на работоспособность, страну и скорость. Парсинг с сайтов.",
    version="2.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

_last_results: List[ProxyResult] = []
_last_checked: Optional[datetime] = None


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "results": _last_results,
        "checked_at": _last_checked.isoformat() if _last_checked else None,
        "working_count": sum(1 for r in _last_results if r.is_working),
        "total_count": len(_last_results)
    })


@app.post("/api/check", response_model=CheckResponse)
async def api_check(payload: CheckRequest):
    global _last_results, _last_checked
    if not payload.proxies:
        raise HTTPException(status_code=400, detail="No proxies provided")

    results = await check_proxies(
        payload.proxies,
        timeout=payload.timeout or 15,
        do_download=payload.download_test if payload.download_test is not None else True
    )
    _last_results = results
    _last_checked = datetime.utcnow()

    working = [r for r in results if r.is_working]
    failed = [r for r in results if not r.is_working]

    return CheckResponse(
        total=len(results),
        working=len(working),
        failed=len(failed),
        results=results,
        checked_at=_last_checked
    )


@app.post("/api/check/file")
async def api_check_file(
    file: UploadFile = File(...),
    timeout: int = Form(15),
    download_test: bool = Form(True)
):
    global _last_results, _last_checked
    content = await file.read()
    lines = content.decode("utf-8").splitlines()

    results = await check_proxies(lines, timeout=timeout, do_download=download_test)
    _last_results = results
    _last_checked = datetime.utcnow()

    working = [r for r in results if r.is_working]
    failed = [r for r in results if not r.is_working]

    return CheckResponse(
        total=len(results),
        working=len(working),
        failed=len(failed),
        results=results,
        checked_at=_last_checked
    )


@app.post("/api/parse", response_model=ParseResponse)
async def api_parse(payload: ParseRequest):
    """Спарсить прокси с сайтов, проверить и вернуть результаты."""
    global _last_results, _last_checked

    parsed = await fetch_all_proxies()
    if payload.max_proxies:
        parsed = parsed[:payload.max_proxies]

    if not parsed:
        raise HTTPException(status_code=503, detail="Не удалось спарсить прокси ни с одного источника")

    results = await check_proxies(
        parsed,
        timeout=payload.timeout or 15,
        do_download=payload.download_test if payload.download_test is not None else True
    )
    _last_results = results
    _last_checked = datetime.utcnow()

    working = [r for r in results if r.is_working]
    failed = [r for r in results if not r.is_working]

    return ParseResponse(
        parsed_count=len(parsed),
        checked_count=len(results),
        working=len(working),
        failed=len(failed),
        results=results,
        checked_at=_last_checked
    )


@app.get("/api/results")
async def api_results():
    return {
        "checked_at": _last_checked.isoformat() if _last_checked else None,
        "total": len(_last_results),
        "working": sum(1 for r in _last_results if r.is_working),
        "results": [
            {
                "host": r.host,
                "port": r.port,
                "country": r.country,
                "country_code": r.country_code,
                "latency_ms": r.latency_ms,
                "download_speed_kbps": r.download_speed_kbps,
                "is_working": r.is_working,
                "error": r.error
            }
            for r in _last_results
        ]
    }


@app.get("/api/results/working")
async def api_working_proxies():
    working = [r for r in _last_results if r.is_working]
    return {
        "count": len(working),
        "proxies": [f"{r.host}:{r.port}" for r in working]
    }


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
