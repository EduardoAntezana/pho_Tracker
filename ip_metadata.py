"""
Metadatos aproximados basados en la IP pública (uso educativo).
La geolocalización por IP es aproximada y suele corresponder al ISP, no al dispositivo físico.
"""

from __future__ import annotations

import json
from typing import Any

import requests

IPIFY_URL = "https://api.ipify.org"
IPINFO_URL = "https://ipinfo.io/json"
TIMEOUT_SEC = 10


def _get_public_ip_ipify() -> str:
    r = requests.get(f"{IPIFY_URL}?format=json", timeout=TIMEOUT_SEC)
    r.raise_for_status()
    data = r.json()
    return str(data.get("ip", "")).strip()


def fetch_ip_metadata() -> dict[str, Any]:
    """
    Obtiene IP pública y metadatos (ciudad, país, ISP) vía ipinfo.io.
    Si ipinfo falla, intenta al menos la IP con ipify.
    """
    result: dict[str, Any] = {
        "ok": False,
        "error": None,
        "ip": None,
        "city": None,
        "region": None,
        "country": None,
        "isp": None,
        "loc": None,
        "raw": None,
    }

    try:
        r = requests.get(IPINFO_URL, timeout=TIMEOUT_SEC)
        r.raise_for_status()
        data = r.json()
        result["ok"] = True
        result["ip"] = data.get("ip")
        result["city"] = data.get("city")
        result["region"] = data.get("region")
        result["country"] = data.get("country")
        result["isp"] = data.get("org")
        result["loc"] = data.get("loc")
        result["raw"] = data
        return result
    except (requests.RequestException, json.JSONDecodeError) as exc:
        result["error"] = str(exc)

    try:
        ip = _get_public_ip_ipify()
        if ip:
            result["ok"] = True
            result["ip"] = ip
            if result["error"]:
                result["error"] = (
                    f"ipinfo.io no disponible ({result['error']}). "
                    "Solo se obtuvo la IP con ipify."
                )
            return result
    except (requests.RequestException, json.JSONDecodeError, KeyError) as exc:
        if not result["error"]:
            result["error"] = str(exc)
        else:
            result["error"] = f"{result['error']}; ipify: {exc}"

    return result
