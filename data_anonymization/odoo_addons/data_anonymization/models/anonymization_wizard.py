import base64
import json
import os
from io import BytesIO
from pathlib import Path

import requests

from odoo import fields, models, _
from odoo.exceptions import UserError


class DataAnonymizationWizard(models.TransientModel):
    _name = "data.anonymization.wizard"
    _description = "Data Anonymization Wizard"

    filename = fields.Char(string="Nama File")
    source_file = fields.Binary(string="File Asli", required=True, attachment=False)
    line_ids = fields.One2many(
        "data.anonymization.wizard.line", "wizard_id", string="Kolom File"
    )
    columns_detected = fields.Boolean(default=False)
    result_file = fields.Binary(string="File Hasil", attachment=False)
    result_filename = fields.Char(string="Nama File Hasil")

    def _get_service_config(self):
        params = self.env["ir.config_parameter"].sudo()
        service_url = (
            os.getenv("ANONYMIZER_SERVICE_URL")
            or params.get_param("data_anonymization.service_url", "http://127.0.0.1:8000")
        ).rstrip("/")
        # The client API key is generated in the API Keys UI and shown only once.
        # Store the selected integration key here as a protected system parameter
        # or supply it through ANONYMIZER_CLIENT_API_KEY in the Odoo process env.
        api_key = (
            os.getenv("ANONYMIZER_CLIENT_API_KEY")
            or params.get_param("data_anonymization.api_key", "")
        )
        if not api_key:
            raise UserError(_("API key FastAPI belum dikonfigurasi."))
        return service_url, {"X-API-Key": api_key}

    def _get_source_bytes(self):
        self.ensure_one()
        if not self.source_file:
            raise UserError(_("Silakan upload file terlebih dahulu."))
        try:
            content = base64.b64decode(self.source_file, validate=True)
        except Exception as exc:
            raise UserError(_("Isi file upload tidak valid.")) from exc
        if not content:
            raise UserError(_("File yang diupload kosong."))
        if len(content) > 10 * 1024 * 1024:
            raise UserError(_("Ukuran file maksimal untuk prototipe adalah 10 MB."))
        return content

    def _post_service(self, endpoint, content, extra_data=None, timeout=(5, 60)):
        service_url, headers = self._get_service_config()
        files = {
            "file": (
                self.filename or "upload.csv",
                BytesIO(content),
                "application/octet-stream",
            )
        }
        try:
            response = requests.post(
                f"{service_url}/{endpoint}",
                headers=headers,
                files=files,
                data=extra_data or {},
                timeout=timeout,
            )
        except requests.RequestException as exc:
            raise UserError(
                _("Tidak dapat menghubungi FastAPI. Periksa URL dan jaringan.")
            ) from exc
        if not response.ok:
            try:
                detail = response.json().get("detail", "")
            except ValueError:
                detail = ""
            raise UserError(_("FastAPI gagal: %s") % detail)
        return response

    def action_inspect_columns(self):
        self.ensure_one()
        content = self._get_source_bytes()
        response = self._post_service("inspect", content)
        try:
            columns = response.json().get("columns", [])
            names = [column["name"] for column in columns]
        except (ValueError, TypeError, KeyError) as exc:
            raise UserError(_("Respons FastAPI tidak valid.")) from exc
        if not names:
            raise UserError(_("Tidak ditemukan kolom dalam file."))

        self.write({
            "columns_detected": True,
            "result_file": False,
            "result_filename": False,
            "line_ids": [
                (5, 0, 0),
                *[
                    (0, 0, {
                        "field_name": name,
                        "selected": False,
                        "method": "mask",
                    })
                    for name in names
                ],
            ],
        })
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_anonymize(self):
        self.ensure_one()
        content = self._get_source_bytes()
        selected = self.line_ids.filtered(lambda line: line.selected)
        if not selected:
            raise UserError(_("Pilih minimal satu kolom untuk dianonimkan."))
        rules = [{"field": line.field_name, "method": line.method} for line in selected]
        response = self._post_service(
            "anonymize",
            content,
            extra_data={"rules_json": json.dumps(rules)},
            timeout=(5, 120),
        )
        extension = Path(self.filename or "data.csv").suffix.lower()
        if extension in (".xlsx", ".xlsm"):
            extension = ".xlsx"
        if extension not in (".csv", ".xlsx"):
            raise UserError(_("Format file tidak didukung."))
        self.write({
            "result_file": base64.b64encode(response.content),
            "result_filename": f"{Path(self.filename or 'data').stem}_anonymized{extension}",
        })
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_download_result(self):
        self.ensure_one()
        if not self.result_file:
            raise UserError(_("Belum ada file hasil. Jalankan proses terlebih dahulu."))
        return {
            "type": "ir.actions.act_url",
            "url": (
                f"/web/content?model={self._name}&id={self.id}"
                f"&field=result_file&filename_field=result_filename&download=true"
            ),
            "target": "self",
        }


class DataAnonymizationWizardLine(models.TransientModel):
    _name = "data.anonymization.wizard.line"
    _description = "Data Anonymization Column"

    wizard_id = fields.Many2one(
        "data.anonymization.wizard", required=True, ondelete="cascade"
    )
    field_name = fields.Char(string="Nama Kolom", required=True, readonly=True)
    selected = fields.Boolean(string="Anonimkan", default=False)
    method = fields.Selection(
        [
            ("mask", "Masking (3 Karakter Pertama)"),
            ("encrypt", "Encryption"),
            ("uuid", "UUID"),
        ],
        string="Metode",
        required=True,
        default="mask",
    )
