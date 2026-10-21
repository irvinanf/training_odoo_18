"""Post-migration for module version 18.0.1.1.0.

The module does not import customer data or create API keys automatically.
API keys must be generated explicitly by an Odoo administrator.
"""


def migrate(cr, version):
    # Safe no-op for the initial module version.
    return
