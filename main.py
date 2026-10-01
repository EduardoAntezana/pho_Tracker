"""
Aplicación educativa: análisis de número telefónico y metadatos por IP pública.

Propósito didáctico sobre formatos E.164, validación y límites de la geolocalización por IP.
No sustituye herramientas forenses ni el consentimiento del usuario para el tratamiento de datos.
"""

from __future__ import annotations

import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

from ip_metadata import fetch_ip_metadata
from phone_analysis import analyze_phone_number


def print_phone_report(data: dict) -> None:
    print("\n--- Análisis del número telefónico ---")
    if not data.get("valid"):
        print(f"Estado: no válido\nMotivo: {data.get('error', 'desconocido')}")
        if data.get("parsed_preview"):
            print(f"Vista previa formateada: {data['parsed_preview']}")
        return

    print("Estado: válido")
    print(f"Formato internacional: {data['formatted_international']}")
    print(f"Formato nacional:      {data['formatted_national']}")
    print(f"Formato E.164:         {data['formatted_e164']}")
    print(f"Código de país (numeración): +{data['country_calling_code']}")
    print(f"Código de región ISO:       {data['region_code']}")
    print(f"Región / zona (geocoder):   {data['region_description']}")
    print(f"Operador (carrier):         {data['carrier_name']}")


def print_ip_report(data: dict) -> None:
    print("\n--- Metadatos por IP pública (aproximados) ---")
    if not data.get("ok"):
        print(f"No se pudieron obtener datos: {data.get('error', 'error desconocido')}")
        return

    print(f"IP pública:     {data.get('ip')}")
    print(f"Ciudad:         {data.get('city') or '(no indicada)'}")
    print(f"Región / estado:{data.get('region') or '(no indicado)'}")
    print(f"País (código):  {data.get('country') or '(no indicado)'}")
    print(f"ISP / org:      {data.get('isp') or '(no indicado)'}")
    if data.get("loc"):
        print(f"Coord. aprox.:  {data['loc']} (lat,lon según ipinfo)")


def run_interactive() -> None:
    print("Rastreador educativo (número + IP)\n")
    raw = input("Introduce un número (con + y código de país, ej. +34612345678): ").strip()
    region_default = input(
        "Si el número es nacional sin +, indica código ISO de país (ej. ES) [Enter para omitir]: "
    ).strip() or None

    print_phone_report(analyze_phone_number(raw, default_region=region_default))

    print("\nConsultando servicios externos (ipinfo / ipify)...")
    print_ip_report(fetch_ip_metadata())


def main() -> int:
    if len(sys.argv) >= 2:
        number = sys.argv[1]
        region = sys.argv[2] if len(sys.argv) >= 3 else None
        print_phone_report(analyze_phone_number(number, default_region=region))
        print_ip_report(fetch_ip_metadata())
        return 0

    run_interactive()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
