# Odoo module migrations

Migration scripts follow Odoo's versioned migration convention:

```
migrations/
└── 18.0.1.1.0/
    ├── pre-migration.py
    └── post-migration.py
```

These scripts are safe no-op examples for the first module version; they do not migrate customer records. Update the module version in `__manifest__.py` when introducing a new migration, and add a new version directory with a clear pre/post migration plan.

Do not put API keys, encryption keys, real customer records, or production database dumps in this directory. Test every migration on a database backup before production deployment.
