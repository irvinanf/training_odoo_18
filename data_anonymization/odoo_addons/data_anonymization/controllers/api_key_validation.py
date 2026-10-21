import hmac
import os

from odoo import http
from odoo.http import request


class DataAnonymizationApiKeyController(http.Controller):

    @http.route(
        "/data-anonymization/internal/validate-api-key",
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def validate_api_key(self, api_key=None, **kwargs):
        expected_secret = os.getenv("ANONYMIZER_VALIDATION_SECRET", "")
        supplied_secret = request.httprequest.headers.get(
            "X-Internal-Validation-Secret", ""
        )
        if (
            not expected_secret
            or not supplied_secret
            or not hmac.compare_digest(supplied_secret, expected_secret)
        ):
            return {"valid": False}

        valid = request.env[
            "data.anonymization.api.key"
        ].sudo().validate_plain_key(api_key)
        return {"valid": bool(valid)}
