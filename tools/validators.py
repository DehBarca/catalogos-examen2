"""Manual request payload validators used by route handlers."""

import re
from typing import Any, Dict, List, Optional

from fastapi import HTTPException

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _bad_request(detail: str) -> None:
    """Raise a standardized HTTP 400 error with the provided detail."""
    raise HTTPException(status_code=400, detail=detail)


def _required_non_empty_string(payload: Dict[str, Any], field: str) -> str:
    """Read and validate a required, non-empty string field from a payload."""
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        _bad_request(f"Campo invalido: {field}")
    return value.strip()


def _optional_email(value: Any, field: str) -> Optional[str]:
    """Validate an optional email value and normalize whitespace."""
    if value is None:
        return None
    if not isinstance(value, str) or not EMAIL_REGEX.match(value.strip()):
        _bad_request(f"Campo invalido: {field}")
    return value.strip()


def validate_client_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize the payload for client creation/update."""
    if not isinstance(payload, dict):
        _bad_request("Body invalido")

    email = _required_non_empty_string(payload, "email")
    if not EMAIL_REGEX.match(email):
        _bad_request("Campo invalido: email")

    return {
        "razon_social": _required_non_empty_string(payload, "razon_social"),
        "nombre_comercial": _required_non_empty_string(payload, "nombre_comercial"),
        "rfc": _required_non_empty_string(payload, "rfc"),
        "email": email,
        "telefono": _required_non_empty_string(payload, "telefono"),
    }


def validate_client_partial_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a partial client payload for PATCH updates."""
    if not isinstance(payload, dict):
        _bad_request("Body invalido")
    if not payload:
        _bad_request("Body invalido: se requiere al menos un campo")

    allowed_fields = {
        "razon_social",
        "nombre_comercial",
        "rfc",
        "email",
        "telefono",
    }
    invalid_fields = [field for field in payload if field not in allowed_fields]
    if invalid_fields:
        _bad_request(f"Campos no permitidos: {', '.join(invalid_fields)}")

    result: Dict[str, Any] = {}
    for field in payload:
        value = _required_non_empty_string(payload, field)
        if field == "email" and not EMAIL_REGEX.match(value):
            _bad_request("Campo invalido: email")
        result[field] = value

    return result


def validate_address_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize the payload for address creation/update."""
    if not isinstance(payload, dict):
        _bad_request("Body invalido")

    tipo = _required_non_empty_string(payload, "tipo_direccion").upper()
    if tipo not in {"FACTURACION", "ENVIO"}:
        _bad_request("Campo invalido: tipo_direccion")

    return {
        "domicilio": _required_non_empty_string(payload, "domicilio"),
        "colonia": _required_non_empty_string(payload, "colonia"),
        "municipio": _required_non_empty_string(payload, "municipio"),
        "estado": _required_non_empty_string(payload, "estado"),
        "tipo_direccion": tipo,
    }


def validate_product_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize the payload for product creation/update."""
    if not isinstance(payload, dict):
        _bad_request("Body invalido")

    raw_price = payload.get("precio_base")
    try:
        price = float(raw_price)
    except (TypeError, ValueError):
        _bad_request("Campo invalido: precio_base")

    if price <= 0:
        _bad_request("Campo invalido: precio_base")

    return {
        "nombre": _required_non_empty_string(payload, "nombre"),
        "unidad_medida": _required_non_empty_string(payload, "unidad_medida"),
        "precio_base": round(price, 2),
    }


def _validate_note_item(item: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Validate a single note line item and return a normalized structure."""
    if not isinstance(item, dict):
        _bad_request(f"Item invalido en posicion {index}")

    product_id = _required_non_empty_string(item, "product_id")

    raw_qty = item.get("cantidad")
    if not isinstance(raw_qty, int) or raw_qty <= 0:
        _bad_request(f"Cantidad invalida en posicion {index}")

    raw_unit_price = item.get("precio_unitario")
    unit_price = None
    if raw_unit_price is not None:
        try:
            unit_price = float(raw_unit_price)
        except (TypeError, ValueError):
            _bad_request(f"Precio unitario invalido en posicion {index}")
        if unit_price <= 0:
            _bad_request(f"Precio unitario invalido en posicion {index}")
        unit_price = round(unit_price, 2)

    return {
        "product_id": product_id,
        "cantidad": raw_qty,
        "precio_unitario": unit_price,
    }


def validate_note_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize the payload for note creation."""
    if not isinstance(payload, dict):
        _bad_request("Body invalido")

    raw_items = payload.get("items")
    if not isinstance(raw_items, list) or not raw_items:
        _bad_request("Campo invalido: items")

    items: List[Dict[str, Any]] = []
    for index, item in enumerate(raw_items):
        items.append(_validate_note_item(item, index))

    return {
        "folio": _required_non_empty_string(payload, "folio"),
        "client_id": _required_non_empty_string(payload, "client_id"),
        "billing_address_id": _required_non_empty_string(payload, "billing_address_id"),
        "shipping_address_id": _required_non_empty_string(payload, "shipping_address_id"),
        "items": items,
    }


def validate_send_note_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate optional payload used when re-sending note notifications."""
    if payload is None:
        return {"email": None}
    if not isinstance(payload, dict):
        _bad_request("Body invalido")
    email = _optional_email(payload.get("email"), "email")
    return {"email": email}


def validate_notification_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the payload for the standalone notification service."""
    if not isinstance(payload, dict):
        _bad_request("Body invalido")

    return {
        "folio": _required_non_empty_string(payload, "folio"),
        "email": _required_non_empty_string(payload, "email"),
        "download_url": _required_non_empty_string(payload, "download_url"),
    }
