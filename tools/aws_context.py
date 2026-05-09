"""Centralized AWS clients/resources and JSON conversion helpers."""

import os
from decimal import Decimal
from typing import Any

import boto3


class AwsContext:
    """Expose configured AWS clients and table names from environment variables."""

    def __init__(self) -> None:
        """Initialize boto3 clients/resources and load runtime configuration."""
        region = "us-east-1"
        self.dynamodb_resource = boto3.resource("dynamodb", region_name=region)
        self.dynamodb_client = boto3.client("dynamodb", region_name=region)
        self.s3 = boto3.client("s3", region_name=region)
        self.sns = boto3.client("sns", region_name=region)
        self.cloudwatch = boto3.client("cloudwatch", region_name=region)

        self.table_clients = os.getenv("TABLE_CLIENTS", "clients")
        self.table_addresses = os.getenv("TABLE_ADDRESSES", "addresses")
        self.table_products = os.getenv("TABLE_PRODUCTS", "products")
        self.table_notes = os.getenv("TABLE_NOTES", "notes")
        self.table_note_items = os.getenv("TABLE_NOTE_ITEMS", "note_items")

        self.bucket_name = os.getenv("BUCKET_NAME", "750519-esi3898l-examen2")
        # Hardcoded SNS Topic ARN (will be used if no env override is provided)
        self.sns_topic_arn = os.getenv(
            "SNS_TOPIC_ARN",
            "arn:aws:sns:us-east-1:828936183282:examen1-750519:4395a2f4-53e5-403a-a5b4-994cb5fd276b",
        )
        self.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        self.app_environment = os.getenv("APP_ENV", os.getenv("ENVIRONMENT", "local"))
        # Use the namespace from .env.example as default and force metrics enabled
        self.metrics_namespace = os.getenv("METRICS_NAMESPACE", "Examen2/SalesNotes")
        self.metrics_enabled = True

    def table(self, table_name: str):
        """Return a DynamoDB Table resource for the provided table name."""
        return self.dynamodb_resource.Table(table_name)


aws = AwsContext()


def to_plain_json(value: Any) -> Any:
    """Convert Decimal values recursively into JSON-serializable ints/floats."""
    if isinstance(value, list):
        return [to_plain_json(v) for v in value]
    if isinstance(value, dict):
        return {k: to_plain_json(v) for k, v in value.items()}
    if isinstance(value, Decimal):
        if value % 1 == 0:
            return int(value)
        return float(value)
    return value
