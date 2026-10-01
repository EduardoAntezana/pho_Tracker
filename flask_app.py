"""
Servidor Flask local: muestra geolocalización por IP y permite una lectura
más precisa vía Geolocation API del navegador (con consentimiento del usuario).

Ejecutar: python flask_app.py
Abrir en el navegador: http://127.0.0.1:5000
"""

from __future__ import annotations

import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

from flask import Flask, jsonify, render_template, request

from ip_metadata import fetch_ip_metadata

app = Flask(__name__)

# Última posición enviada por el cliente (solo en memoria; se pierde al reiniciar).
_last_browser_fix: dict | None = None


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/api/ip")
def api_ip():
    return jsonify(fetch_ip_metadata())


@app.post("/api/browser-location")
def api_browser_location():
    global _last_browser_fix
    payload = request.get_json(silent=True) or {}

    try:
        lat = float(payload["latitude"])
        lon = float(payload["longitude"])
    except (KeyError, TypeError, ValueError):
        return (
            jsonify(
                {
                    "ok": False,
                    "error": "Se requieren latitude y longitude numéricos.",
                }
            ),
            400,
        )

    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return (
            jsonify({"ok": False, "error": "Coordenadas fuera de rango."}),
            400,
        )

    accuracy = payload.get("accuracy")
    if accuracy is not None:
        try:
            accuracy = float(accuracy)
        except (TypeError, ValueError):
            accuracy = None

    fix = {
        "latitude": lat,
        "longitude": lon,
        "accuracy_m": accuracy,
        "altitude_m": payload.get("altitude"),
        "heading": payload.get("heading"),
        "speed": payload.get("speed"),
    }
    _last_browser_fix = fix
    print(f"[geolocalización navegador] lat={lat} lon={lon} precisión≈{accuracy} m")
    return jsonify({"ok": True, "received": fix})


@app.get("/api/browser-location/latest")
def api_browser_location_latest():
    if _last_browser_fix is None:
        return (
            jsonify({"ok": False, "error": "Aún no se ha enviado ninguna posición."}),
            404,
        )
    return jsonify({"ok": True, **_last_browser_fix})


if __name__ == "__main__":
    print("Servidor: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
