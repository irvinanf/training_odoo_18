"""Pre-migration for module version 18.0.1.1.0.

This starter migration intentionally does not modify existing business tables.
Odoo creates the module's own model tables from the model definitions.
Use this hook for future controlled schema/data migrations when upgrading versions.
"""


def migrate(cr, version):
    # No destructive changes are required for the initial installation.
    return
