# Data Anonymization — Odoo 18 + FastAPI

This folder is a standalone project inside the existing `training_odoo_18` repository. It does not replace or modify the existing training modules.

## Features
- Odoo wizard: upload CSV/XLSX, inspect columns, select per-column masking/encryption/UUID, download result.
- API key management in Odoo: generate, list, revoke/reactivate, edit metadata, delete.
- FastAPI validates client API keys against Odoo before processing requests.
- Development runs without Docker. Dockerfile and a FastAPI-only Compose example are provided for production.

## Layout
- `odoo_addons/data_anonymization`: Odoo custom module.
- `anonymizer_service`: FastAPI service.

## 1. Start FastAPI locally
Use a Python virtual environment in `data_anonymization/anonymizer_service`.

Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
Copy-Item .env.example .env
```

Linux/macOS:
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
cp .env.example .env
```

Edit `.env`:
- `FERNET_KEY`: generated Fernet key.
- `ANONYMIZER_VALIDATION_SECRET`: a long random service-to-service secret.
- `ANONYMIZER_ODOO_VALIDATION_URL`: internal Odoo URL ending in `/data-anonymization/internal/validate-api-key`.

Generate the internal secret with:
```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```
Set the same `ANONYMIZER_VALIDATION_SECRET` in the environment of the Odoo process. Do not use a client API key for this secret.

Run:
```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Test `http://127.0.0.1:8000/health` and `http://127.0.0.1:8000/docs`.

## 2. Install the Odoo module
Copy `odoo_addons/data_anonymization` into the custom addons directory already used by your Odoo repository. Ensure that directory is included in the existing `addons_path`; do not replace existing paths. Ensure Python package `requests` is installed in the Python environment used by Odoo.

Restart Odoo, enable Developer Mode, update Apps List, then install or upgrade module `data_anonymization`.

## 3. Configure Odoo
In Odoo System Parameters set:
- `data_anonymization.service_url` = `http://127.0.0.1:8000` for local development if both processes run on the same host.

If Odoo and FastAPI run in separate containers, use a URL reachable from the Odoo container. If both containers share a Docker network, use the FastAPI service name. The FastAPI-to-Odoo validation URL must similarly be reachable from FastAPI.

Set `ANONYMIZER_VALIDATION_SECRET` in the Odoo process environment and FastAPI `.env` to the same value.

## 4. Create an API key
As an Odoo administrator:
1. Open **Data Tools → Generate API Key**.
2. Enter a descriptive name and optional expiry.
3. Generate and copy the secret immediately; the secret is not stored in plaintext in the permanent API key model.
4. Open **Data Tools → API Keys** to view metadata, revoke/reactivate, edit metadata, or delete a key.

The generated client key is sent to FastAPI in the `X-API-Key` header. FastAPI asks Odoo to validate it on every request. If Odoo is unavailable, validation fails closed (503).

## 5. End-to-end test
Create a CSV with dummy data:
```csv
Customer Name,Phone,Email
Budi Santoso,081234567890,budi@example.test
Siti Aminah,082112345678,siti@example.test
Budi Santoso,081234567890,budi@example.test
```
In Odoo: Data Tools → Data Anonymization → upload → Inspect Columns → choose methods → Run Anonymization → Download Result.

Methods:
- `mask`: keep first three characters and replace the rest with `*`. Values of length 3 or less remain unchanged in this starter version.
- `encrypt`: Fernet authenticated encryption; output is not readable as the original value and requires the same key to decrypt.
- `uuid`: values are consistent within the same column and request only. Mapping is in memory and is not persisted, so deanonymization/cross-file consistency is not included yet.

## Security and limitations
- Start with dummy data. This is a starter implementation, not a production security certification.
- Never commit `.env`, API keys, Fernet keys, or real customer data.
- Odoo is a runtime dependency for API key validation. Restrict the internal validation endpoint to the service network and protect it with the internal secret.
- Use HTTPS for traffic across untrusted networks.
- Odoo transient wizard binaries are stored temporarily in the Odoo database. Review access rights, retention, backups, and cleanup.
- File size is limited to 10 MB and processing is in memory. Do not increase the limit without capacity tests.
- XLSM input produces XLSX output; macros, styles, formulas, and workbook metadata are not guaranteed to be preserved.
- UUID mapping is not persisted and cannot be used to restore original values.
- Before production, add malware scanning, audit controls, rate limiting, request-size limits at proxy level, monitoring, secret manager integration, and tests against your exact Odoo deployment.

## Production container
Build/run the FastAPI service using `Dockerfile` and `docker-compose.production.example.yml`. The example is intentionally limited to FastAPI and must be attached to the existing Odoo network according to your deployment. It does not replace your existing Odoo Compose stack.
