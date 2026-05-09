"""REST endpoints for client CRUD operations."""

from uuid import uuid4
from typing import Optional

from fastapi import APIRouter, Body, HTTPException
from boto3.dynamodb.conditions import Attr

from tools.aws_context import aws, to_plain_json
from tools.validators import validate_client_partial_payload, validate_client_payload

router = APIRouter(prefix="/clients", tags=["clients"])


def _ensure_unique_client_fields(table, rfc: str, razon_social: str, exclude_id: Optional[str] = None) -> None:
    """Ensure RFC and razon_social are unique across clients table."""
    if exclude_id:
        filter_expr = (Attr("id").ne(exclude_id)) & (
            Attr("rfc").eq(rfc) | Attr("razon_social").eq(razon_social)
        )
    else:
        filter_expr = Attr("rfc").eq(rfc) | Attr("razon_social").eq(razon_social)

    response = table.scan(FilterExpression=filter_expr, Limit=1)
    existing = response.get("Items", [])
    if existing:
        item = existing[0]
        if item.get("rfc") == rfc:
            raise HTTPException(status_code=409, detail="RFC ya registrado")
        if item.get("razon_social") == razon_social:
            raise HTTPException(status_code=409, detail="Razon social ya registrada")


@router.post("")
def create_client(payload: dict = Body(...)):
    """Create a new client and store it in DynamoDB."""
    table = aws.table(aws.table_clients)
    client_id = str(uuid4())
    data = validate_client_payload(payload)
    _ensure_unique_client_fields(table, data["rfc"], data["razon_social"])
    item = {"id": client_id, **data}
    table.put_item(Item=item)
    return item


@router.get("/{client_id}")
def get_client(client_id: str):
    """Fetch a client by its identifier."""
    response = aws.table(aws.table_clients).get_item(Key={"id": client_id})
    item = response.get("Item")
    if not item:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return to_plain_json(item)


@router.put("/{client_id}")
def update_client(client_id: str, payload: dict = Body(...)):
    """Replace the full client payload for a given identifier."""
    table = aws.table(aws.table_clients)
    existing = table.get_item(Key={"id": client_id}).get("Item")
    if not existing:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    data = validate_client_payload(payload)
    _ensure_unique_client_fields(table, data["rfc"], data["razon_social"], exclude_id=client_id)
    item = {"id": client_id, **data}
    table.put_item(Item=item)
    return item


@router.patch("/{client_id}")
def patch_client(client_id: str, payload: dict = Body(...)):
    """Partially update a client with only the provided fields."""
    table = aws.table(aws.table_clients)
    existing = table.get_item(Key={"id": client_id}).get("Item")
    if not existing:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    data = validate_client_partial_payload(payload)
    next_rfc = data.get("rfc", existing["rfc"])
    next_razon_social = data.get("razon_social", existing["razon_social"])
    _ensure_unique_client_fields(table, next_rfc, next_razon_social, exclude_id=client_id)
    existing.update(data)
    table.put_item(Item=existing)
    return existing


@router.delete("/{client_id}")
def delete_client(client_id: str):
    """Delete a client if it exists."""
    table = aws.table(aws.table_clients)
    existing = table.get_item(Key={"id": client_id}).get("Item")
    if not existing:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    table.delete_item(Key={"id": client_id})
    return {"message": "Cliente eliminado"}
