"""REST endpoints for product CRUD operations."""

from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, Body, HTTPException

from tools.aws_context import aws, to_plain_json
from tools.validators import validate_product_payload

router = APIRouter(prefix="/products", tags=["products"])


@router.post("")
def create_product(payload: dict = Body(...)):
    """Create a new product and persist it in DynamoDB."""
    product_id = str(uuid4())
    data = validate_product_payload(payload)
    data["precio_base"] = Decimal(str(data["precio_base"]))
    item = {"id": product_id, **data}
    aws.table(aws.table_products).put_item(Item=item)
    return item


@router.get("/{product_id}")
def get_product(product_id: str):
    """Fetch a product by its identifier."""
    response = aws.table(aws.table_products).get_item(Key={"id": product_id})
    item = response.get("Item")
    if not item:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return to_plain_json(item)


@router.put("/{product_id}")
def update_product(product_id: str, payload: dict = Body(...)):
    """Replace the full product payload for the given identifier."""
    table = aws.table(aws.table_products)
    existing = table.get_item(Key={"id": product_id}).get("Item")
    if not existing:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    data = validate_product_payload(payload)
    data["precio_base"] = Decimal(str(data["precio_base"]))
    item = {"id": product_id, **data}
    table.put_item(Item=item)
    return item


@router.delete("/{product_id}")
def delete_product(product_id: str):
    """Delete a product if it exists."""
    table = aws.table(aws.table_products)
    existing = table.get_item(Key={"id": product_id}).get("Item")
    if not existing:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    table.delete_item(Key={"id": product_id})
    return {"message": "Producto eliminado"}
