import io
import uuid
from pathlib import Path
from typing import Any

import pandas as pd
from cryptography.fernet import Fernet

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xlsm"}
ALLOWED_METHODS = {"mask", "encrypt", "uuid"}


def validate_filename(filename: str | None) -> str:
    extension = Path(filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Format file harus CSV, XLSX, atau XLSM.")
    return extension


def read_dataframe(file_bytes: bytes, extension: str) -> pd.DataFrame:
    if not file_bytes:
        raise ValueError("File kosong.")
    if extension == ".csv":
        df = pd.read_csv(
            io.BytesIO(file_bytes),
            dtype=str,
            keep_default_na=False,
            encoding="utf-8-sig",
        )
    else:
        df = pd.read_excel(
            io.BytesIO(file_bytes),
            dtype=object,
            keep_default_na=False,
            engine="openpyxl",
        )

    if len(df.columns) == 0:
        raise ValueError("File tidak memiliki kolom.")
    if len(df.columns) > 200:
        raise ValueError("Maksimal 200 kolom per file.")
    columns = [str(c) for c in df.columns]
    if any(not c.strip() for c in columns):
        raise ValueError("Nama kolom tidak boleh kosong.")
    if len(columns) != len(set(columns)):
        raise ValueError("Nama kolom harus unik. Periksa header file.")
    df.columns = columns
    return df


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def mask_value(value: Any) -> Any:
    if _is_empty(value):
        return value
    text = str(value)
    return text if len(text) <= 3 else text[:3] + ("*" * (len(text) - 3))


def encrypt_value(value: Any, cipher: Fernet) -> Any:
    if _is_empty(value) or value == "":
        return value
    return cipher.encrypt(str(value).encode("utf-8")).decode("ascii")


def uuid_value(value: Any, mapping: dict[str, str]) -> Any:
    if _is_empty(value) or value == "":
        return value
    text = str(value)
    if text not in mapping:
        mapping[text] = str(uuid.uuid4())
    return mapping[text]


def anonymize_dataframe(
    df: pd.DataFrame, rules: list[dict[str, str]], fernet_key: str
) -> pd.DataFrame:
    if not isinstance(rules, list) or not rules:
        raise ValueError("Pilih minimal satu kolom untuk diproses.")

    seen_fields: set[str] = set()
    for rule in rules:
        if not isinstance(rule, dict):
            raise ValueError("Format aturan tidak valid.")
        field, method = rule.get("field"), rule.get("method")
        if not isinstance(field, str) or field not in df.columns:
            raise ValueError(f"Kolom tidak ditemukan: {field}")
        if method not in ALLOWED_METHODS:
            raise ValueError(f"Metode tidak valid: {method}")
        if field in seen_fields:
            raise ValueError(f"Kolom dipilih lebih dari sekali: {field}")
        seen_fields.add(field)

    try:
        cipher = Fernet(fernet_key.encode("ascii"))
    except Exception as exc:
        raise ValueError("Kunci Fernet tidak valid.") from exc

    result = df.copy()
    mappings: dict[str, dict[str, str]] = {}
    for rule in rules:
        field, method = rule["field"], rule["method"]
        if method == "mask":
            result[field] = result[field].map(mask_value)
        elif method == "encrypt":
            result[field] = result[field].map(
                lambda value: encrypt_value(value, cipher)
            )
        else:
            mapping = mappings.setdefault(field, {})
            result[field] = result[field].map(
                lambda value: uuid_value(value, mapping)
            )
    return result


def dataframe_to_bytes(
    df: pd.DataFrame, input_extension: str
) -> tuple[bytes, str, str]:
    output = io.BytesIO()
    if input_extension == ".csv":
        df.to_csv(output, index=False, encoding="utf-8-sig")
        return output.getvalue(), "text/csv; charset=utf-8", ".csv"
    df.to_excel(output, index=False, engine="openpyxl")
    return (
        output.getvalue(),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xlsx",
    )
