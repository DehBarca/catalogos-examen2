"""Helper to resolve addresses with composite key schema."""

from typing import Any, Dict, Optional, Tuple


def resolve_address_key_and_item(table: Any, client_id: str, address_id: str) -> Tuple[Dict[str, str], Optional[Dict[str, Any]]]:
    """
    Resolve an address using the composite key (client_id + id).
    
    The addresses table uses:
    - client_id as HASH key (partition key)
    - id as RANGE key (sort key)
    
    Returns:
        tuple: (key_dict, item_or_none)
        - key_dict: The key dictionary for delete/update operations
        - item_or_none: The address item if found, None otherwise
    """
    key = {"client_id": client_id, "id": address_id}
    try:
        response = table.get_item(Key=key)
        return key, response.get("Item")
    except Exception:
        return key, None
