from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ProxyInput(BaseModel):
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None


class ProxyResult(BaseModel):
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    url: str
    country: Optional[str] = None
    country_code: Optional[str] = None
    latency_ms: float
    download_speed_kbps: float
    download_time_ms: float
    is_working: bool
    error: Optional[str] = None
    checked_at: datetime


class CheckRequest(BaseModel):
    proxies: List[str]
    timeout: Optional[int] = 15
    download_test: Optional[bool] = True


class ParseRequest(BaseModel):
    timeout: Optional[int] = 15
    download_test: Optional[bool] = True
    max_proxies: Optional[int] = 200  # лимит на количество


class ParseResponse(BaseModel):
    parsed_count: int
    checked_count: int
    working: int
    failed: int
    results: List[ProxyResult]
    checked_at: datetime


class CheckResponse(BaseModel):
    total: int
    working: int
    failed: int
    results: List[ProxyResult]
    checked_at: datetime
