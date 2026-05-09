"""REST endpoints for managing client addresses."""

from uuid import uuid4

from fastapi import APIRouter, Body, HTTPException

from tools.addresses_repo import resolve_address_key_and_item
from tools.aws_context import aws, to_plain_json
from tools.validators import validate_address_payload

router = APIRouter(prefix="/clients/{client_id}/addresses", tags=["addresses"])


@router.post("")
def create_address(client_id: str, payload: dict = Body(...)):
    """Create a billing or shipping address for an existing client."""
    client = aws.table(aws.table_clients).get_item(Key={"id": client_id}).get("Item")
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    address_id = str(uuid4())
    data = validate_address_payload(payload)
    item = {"client_id": client_id, "id": address_id, **data}
    aws.table(aws.table_addresses).put_item(Item=item)
    return item


@router.get("/{address_id}")
def get_address(client_id: str, address_id: str):
    """Fetch a single address for a specific client."""
    table = aws.table(aws.table_addresses)
    _, item = resolve_address_key_and_item(table, client_id, address_id)
    if not item:
        raise HTTPException(status_code=404, detail="Domicilio no encontrado")
    if item.get("client_id") and item.get("client_id") != client_id:
        raise HTTPException(status_code=404, detail="Domicilio no encontrado para el cliente")
    return to_plain_json(item)


@router.put("/{address_id}")
def update_address(client_id: str, address_id: str, payload: dict = Body(...)):
    """Replace the full address payload for a specific client address."""
    table = aws.table(aws.table_addresses)
    _, existing = resolve_address_key_and_item(table, client_id, address_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Domicilio no encontrado")
    if existing.get("client_id") and existing.get("client_id") != client_id:
        raise HTTPException(status_code=404, detail="Domicilio no encontrado para el cliente")

    data = validate_address_payload(payload)
    item = {"client_id": client_id, "id": address_id, **data}
    table.put_item(Item=item)
    return item


@router.delete("/{address_id}")
def delete_address(client_id: str, address_id: str):
    """Delete a client address if it exists."""
    table = aws.table(aws.table_addresses)
    key, existing = resolve_address_key_and_item(table, client_id, address_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Domicilio no encontrado")
    if existing.get("client_id") and existing.get("client_id") != client_id:
        raise HTTPException(status_code=404, detail="Domicilio no encontrado para el cliente")

    table.delete_item(Key=key)
    return {"message": "Domicilio eliminado"}
