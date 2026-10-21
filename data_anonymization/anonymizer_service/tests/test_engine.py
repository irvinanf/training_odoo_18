import pandas as pd
import pytest
from cryptography.fernet import Fernet

from app.engine import anonymize_dataframe, mask_value


def test_mask_keeps_first_three_characters():
    assert mask_value("Budi Santoso") == "Bud*********"
    assert mask_value("081234") == "081***"
    assert mask_value("ABC") == "ABC"


def test_uuid_same_value_same_uuid_in_same_column():
    key = Fernet.generate_key().decode()
    df = pd.DataFrame({"Phone": ["0812", "0821", "0812"]})
    result = anonymize_dataframe(df, [{"field": "Phone", "method": "uuid"}], key)
    assert result.loc[0, "Phone"] == result.loc[2, "Phone"]
    assert result.loc[0, "Phone"] != result.loc[1, "Phone"]


def test_encrypt_changes_value_and_can_be_decrypted_with_key():
    key = Fernet.generate_key()
    df = pd.DataFrame({"Email": ["person@example.test"]})
    result = anonymize_dataframe(df, [{"field": "Email", "method": "encrypt"}], key.decode())
    assert result.loc[0, "Email"] != "person@example.test"
    assert Fernet(key).decrypt(result.loc[0, "Email"].encode()).decode() == "person@example.test"


def test_invalid_column_rejected():
    key = Fernet.generate_key().decode()
    df = pd.DataFrame({"Name": ["Budi"]})
    with pytest.raises(ValueError, match="Kolom tidak ditemukan"):
        anonymize_dataframe(df, [{"field": "Email", "method": "mask"}], key)
