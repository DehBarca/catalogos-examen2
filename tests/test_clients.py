import sys
import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def test_create_client(monkeypatch):
    class DummyTable:
        def __init__(self):
            self.storage = {}

        def put_item(self, Item):
            self.storage[Item["id"]] = Item

        def get_item(self, Key):
            return {"Item": self.storage.get(Key["id"]) }

        def scan(self, FilterExpression=None, Limit=None):
            return {"Items": []}

    class DummyAws:
        def __init__(self):
            self._table = DummyTable()
            self.table_clients = "clients"

        def table(self, name):
            return self._table

    import tools.aws_context as aws_mod
    aws_mod.aws = DummyAws()

    sys.modules.pop("main", None)
    module_path = Path(__file__).resolve().parents[1] / "main.py"
    spec = importlib.util.spec_from_file_location("catalogs_main_test", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    app = module.app

    client = TestClient(app)
    payload = {
        "razon_social": "Empresa SA",
        "nombre_comercial": "Empresa",
        "rfc": "RFC123",
        "email": "test@example.com",
        "telefono": "555-1234",
    }

    resp = client.post("/clients", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert "id" in body
    assert body["rfc"] == "RFC123"
