"""
Análisis educativo de números telefónicos con libphonenumber (Google).
"""

from __future__ import annotations

import phonenumbers
from phonenumbers import NumberParseException, PhoneNumberFormat, geocoder, carrier


def analyze_phone_number(
    raw_input: str,
    default_region: str | None = None,
    language: str = "es",
) -> dict:
    """
    Valida y describe un número telefónico.

    Args:
        raw_input: Texto del usuario (idealmente en formato E.164, ej. +59170123456).
        default_region: Código ISO de país de dos letras (ej. 'BO') si el número no lleva prefijo +.
        language: Idioma para descripciones de geocoder/carrier.

    Returns:
        Diccionario con claves: valid, error, formatted_international, formatted_national,
        country_calling_code, region_code, region_description, carrier_name.
    """
    text = (raw_input or "").strip()
    if not text:
        return {
            "valid": False,
            "error": "No se ingresó ningún número.",
        }

    try:
        parsed = phonenumbers.parse(text, default_region)
    except NumberParseException as exc:
        return {
            "valid": False,
            "error": f"No se pudo interpretar el número: {exc}",
        }

    if not phonenumbers.is_valid_number(parsed):
        reason = "El número no es válido según las reglas del país."
        if phonenumbers.is_possible_number(parsed):
            reason += " (Es posible pero no válido; revisa dígitos o prefijo.)"
        return {
            "valid": False,
            "error": reason,
            "parsed_preview": phonenumbers.format_number(
                parsed, PhoneNumberFormat.INTERNATIONAL
            ),
        }

    region_code = phonenumbers.region_code_for_number(parsed)
    region_desc = geocoder.description_for_number(parsed, language)
    carrier_name = carrier.name_for_number(parsed, language) or "(no disponible en la base de datos)"

    return {
        "valid": True,
        "error": None,
        "formatted_international": phonenumbers.format_number(
            parsed, PhoneNumberFormat.INTERNATIONAL
        ),
        "formatted_national": phonenumbers.format_number(
            parsed, PhoneNumberFormat.NATIONAL
        ),
        "formatted_e164": phonenumbers.format_number(
            parsed, PhoneNumberFormat.E164
        ),
        "country_calling_code": parsed.country_code,
        "region_code": region_code or "(desconocido)",
        "region_description": region_desc or "(sin descripción de región)",
        "carrier_name": carrier_name,
    }
