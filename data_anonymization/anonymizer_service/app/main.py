import io
import json
import os
from pathlib import Path
from typing import Annotated

import requests
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.engine import anonymize_dataframe, dataframe_to_bytes, read_dataframe, validate_filename

load_dotenv()
app = FastAPI(title="Data Anonymization Service", version="1.0.0")
ODOO_VALIDATION_URL = os.getenv(
    "ANONYMIZER_ODOO_VALIDATION_URL",
    "http://127.0.0.1:8069/data-anonymization/internal/validate-api-key",
)
VALIDATION_SECRET = os.getenv("ANONYMIZER_VALIDATION_SECRET", "")
FERNET_KEY = os.getenv("FERNET_KEY", "")
try:
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", "10")) * 1024 * 1024
except ValueError:
    MAX_FILE_SIZE = 10 * 1024 * 1024


def verify_api_key(x_api_key: Annotated[str, Header()] = "") -> None:
    if not x_api_key or not VALIDATION_SECRET:
        raise HTTPException(status_code=401, detail="API key tidak valid.")
    try:
        # Odoo JSON-RPC controller expects a JSON-RPC envelope.
        response = requests.post(
            ODOO_VALIDATION_URL,
            headers={"X-Internal-Validation-Secret": VALIDATION_SECRET},
            json={
                "jsonrpc": "2.0",
                "method": "call",
                "params": {"api_key": x_api_key},
                "id": 1,
            },
            timeout=(2, 4),
        )
        response.raise_for_status()
        payload = response.json()
        result = payload.get("result", {}) if isinstance(payload, dict) else {}
        valid = bool(result.get("valid")) if isinstance(result, dict) else False
    except (requests.RequestException, ValueError):
        raise HTTPException(
            status_code=503,
            detail="Layanan validasi API key Odoo tidak tersedia.",
        )
    if not valid:
        raise HTTPException(status_code=401, detail="API key tidak valid.")


async def load_upload(file: UploadFile) -> tuple[bytes, str]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nama file tidak tersedia.")
    try:
        extension = validate_filename(file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    content = await file.read(MAX_FILE_SIZE + 1)
    if not content:
        raise HTTPException(status_code=400, detail="File kosong.")
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Ukuran maksimal file adalah {MAX_FILE_SIZE // (1024 * 1024)} MB.",
        )
    return content, extension


def parse_table(content: bytes, extension: str):
    try:
        return read_dataframe(content, extension)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"File tidak dapat dibaca ({type(exc).__name__}).",
        ) from exc


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/inspect", dependencies=[Depends(verify_api_key)])
async def inspect_file(file: Annotated[UploadFile, File()]):
    content, extension = await load_upload(file)
    df = parse_table(content, extension)
    return {
        "filename": Path(file.filename or "upload").name,
        "columns": [{"name": str(column)} for column in df.columns],
        "row_count": len(df),
    }


@app.post("/anonymize", dependencies=[Depends(verify_api_key)])
async def anonymize_file(
    file: Annotated[UploadFile, File()],
    rules_json: Annotated[str, Form()],
):
    if not FERNET_KEY:
        raise HTTPException(status_code=500, detail="Kunci enkripsi belum dikonfigurasi.")
    content, extension = await load_upload(file)
    df = parse_table(content, extension)
    try:
        rules = json.loads(rules_json)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Konfigurasi kolom bukan JSON valid.") from exc
    if not isinstance(rules, list) or not rules:
        raise HTTPException(status_code=400, detail="Pilih minimal satu kolom.")
    try:
        result = anonymize_dataframe(df, rules, FERNET_KEY)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    output_bytes, content_type, output_extension = dataframe_to_bytes(result, extension)
    filename = f"{Path(file.filename or 'data').stem}_anonymized{output_extension}"
    return StreamingResponse(
        io.BytesIO(output_bytes),
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )
