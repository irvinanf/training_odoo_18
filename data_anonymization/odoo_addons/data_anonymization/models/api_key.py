import hashlib
import secrets

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError


def _hash_api_key(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class DataAnonymizationApiKey(models.Model):
    _name = "data.anonymization.api.key"
    _description = "Data Anonymization API Key"
    _order = "create_date desc"

    name = fields.Char(required=True, index=True)
    key_prefix = fields.Char(readonly=True, copy=False)
    key_hash = fields.Char(readonly=True, copy=False, index=True)
    active = fields.Boolean(default=True, index=True)
    expires_at = fields.Datetime()
    last_used_at = fields.Datetime(readonly=True)
    created_by = fields.Many2one(
        "res.users", readonly=True, default=lambda self: self.env.user
    )

    _sql_constraints = [
        ("key_hash_unique", "unique(key_hash)", "API key hash must be unique."),
    ]

    @api.model
    def validate_plain_key(self, plain_key):
        if not plain_key or not isinstance(plain_key, str):
            return False
        record = self.sudo().search([
            ("key_hash", "=", _hash_api_key(plain_key)),
            ("active", "=", True),
        ], limit=1)
        if not record:
            return False
        now = fields.Datetime.now()
        if record.expires_at and record.expires_at <= now:
            return False
        record.sudo().write({"last_used_at": now})
        return True

    def write(self, vals):
        if not self.env.user.has_group("base.group_system"):
            raise AccessError(_("Only administrators can manage API keys."))
        protected = {"key_hash", "key_prefix", "created_by"}
        if protected.intersection(vals):
            raise AccessError(_("Secret key fields cannot be edited manually."))
        return super().write(vals)

    def unlink(self):
        if not self.env.user.has_group("base.group_system"):
            raise AccessError(_("Only administrators can delete API keys."))
        return super().unlink()

    def action_revoke(self):
        if not self.env.user.has_group("base.group_system"):
            raise AccessError(_("Only administrators can manage API keys."))
        self.write({"active": False})
        return True

    def action_reactivate(self):
        if not self.env.user.has_group("base.group_system"):
            raise AccessError(_("Only administrators can manage API keys."))
        self.write({"active": True})
        return True


class DataAnonymizationApiKeyWizard(models.TransientModel):
    _name = "data.anonymization.api.key.wizard"
    _description = "Generate Data Anonymization API Key"

    name = fields.Char(required=True)
    expires_at = fields.Datetime()
    generated_key = fields.Char(readonly=True, copy=False)
    key_created = fields.Boolean(default=False, readonly=True)

    def action_generate(self):
        self.ensure_one()
        if not self.env.user.has_group("base.group_system"):
            raise AccessError(_("Only administrators can manage API keys."))
        if self.key_created:
            raise UserError(
                _("A key has already been generated in this wizard. "
                  "Close this window and create a new key if needed.")
            )

        plain_key = "anon_" + secrets.token_urlsafe(32)
        self.env["data.anonymization.api.key"].sudo().create({
            "name": self.name,
            "key_prefix": plain_key[:12],
            "key_hash": _hash_api_key(plain_key),
            "expires_at": self.expires_at or False,
            "active": True,
            "created_by": self.env.user.id,
        })
        self.write({"generated_key": plain_key, "key_created": True})
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }
