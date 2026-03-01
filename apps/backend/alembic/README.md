# Database Migrations

This directory contains Alembic migrations for the PostgreSQL database.

## Setup

Alembic is configured to work with async SQLAlchemy and PostgreSQL.

## Environment Variables

Set the following environment variables in `.env`:

```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/aidatalabs
DB_ECHO=false  # Set to true to see SQL queries
```

## Running Migrations

### Create a new migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description of changes"

# Create empty migration file
alembic revision -m "description of changes"
```

### Apply migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade <revision_id>

# Rollback one migration
alembic downgrade -1

# Rollback to specific migration
alembic downgrade <revision_id>
```

### View migration status

```bash
# Show current revision
alembic current

# Show all revisions
alembic history

# Show pending migrations
alembic heads
```

## Migration History

- `initial_schema`: Initial database schema with users and sessions tables

## Best Practices

1. Always review auto-generated migrations before applying
2. Write reversible migrations when possible
3. Test migrations on a copy of production data
4. Never modify existing migration files
5. Always add descriptive migration messages
6. Use atomic migrations for small changes
7. Use data migrations for complex data transformations

## Troubleshooting

### Migration fails with "table already exists"

```bash
# Mark migration as complete without running it
alembic stamp head
```

### Need to reset database

```bash
# WARNING: This deletes all data!
alembic downgrade base
alembic upgrade head
```

## ClickHouse Migrations

ClickHouse tables are created programmatically in the application code.
See `src/models/clickhouse/` for table definitions.

To create ClickHouse tables:

```python
from src.models.clickhouse import QueryLog, Metrics

# Create tables
QueryLog.create_table()
Metrics.create_table()
```

## Notes

- Migrations are automatically applied on application startup in production
- Use `alembic revision --autogenerate` after model changes
- Always test migrations locally before deploying
