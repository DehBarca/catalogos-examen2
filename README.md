# Catalogs service

This service manages clients, addresses, and products.

## Environment variables

Use the values from [`.env.example`](.env.example).

## Local run

```powershell
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## CI/CD

The workflow at [`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs tests and publishes a Docker image to GHCR on pushes to `main`.
