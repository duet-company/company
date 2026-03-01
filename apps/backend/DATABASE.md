# Database Setup and Models

## Overview

The AI Data Labs platform uses two database systems:

1. **PostgreSQL** - Primary database for user management, authentication, and application data
2. **ClickHouse** - Analytics database for query logging and metrics

## PostgreSQL Database

### Connection

Environment variables:
```bash
DATABASE_URL=postgresql+asyncpg://aidatalabs:aidatalabs@localhost:5432/aidatalabs
DB_ECHO=false  # Set to true for SQL query logging
```

### Models

#### User Model

```python
from src.models.db import User

# Create user
user = User(
    email="user@example.com",
    full_name="John Doe",
    hashed_password="hashed_password_here",
    role=UserRole.USER,
    is_active=True,
    is_verified=False
)
```

Fields:
- `id` (UUID) - Primary key
- `email` (String) - User email (unique)
- `full_name` (String) - User's full name
- `hashed_password` (String) - Bcrypt hashed password
- `role` (Enum) - User role: admin, user, guest
- `is_active` (Boolean) - Account active status
- `is_verified` (Boolean) - Email verification status
- `created_at` (DateTime) - Account creation timestamp
- `updated_at` (DateTime) - Last update timestamp

#### Session Model

```python
from src.models.db import Session

# Create session
session = Session(
    user_id=user.id,
    token="access_token",
    refresh_token="refresh_token",
    expires_at=datetime.utcnow() + timedelta(hours=24),
    is_revoked=False
)
```

Fields:
- `id` (UUID) - Primary key
- `user_id` (UUID) - Foreign key to users
- `token` (String) - JWT access token
- `refresh_token` (String) - JWT refresh token
- `expires_at` (DateTime) - Token expiration time
- `is_revoked` (Boolean) - Session revocation status
- `created_at` (DateTime) - Session creation timestamp
- `updated_at` (DateTime) - Last update timestamp

### Database Sessions

```python
from sqlalchemy import select
from src.database import get_db

# Using FastAPI dependency
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

# Using context manager
from src.database import get_db_context

async def create_user():
    async with get_db_context() as db:
        user = User(email="user@example.com", full_name="John Doe", ...)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
```

### Migrations

See [alembic/README.md](alembic/README.md) for migration instructions.

## ClickHouse Database

### Connection

Environment variables:
```bash
CLICKHOUSE_URL=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=
CLICKHOUSE_DATABASE=aidatalabs
```

### Models

#### Query Log Model

```python
from src.models.clickhouse import QueryLog

# Initialize ClickHouse table (run once)
QueryLog.create_table()

# Log a query
QueryLog.insert(
    query_id="unique-query-id",
    user_id="user-uuid",
    query_text="SELECT * FROM table",
    query_type="SELECT",
    execution_time_ms=150,
    rows_read=1000,
    bytes_read=50000,
    memory_used=1024,
    status="success",
    error_message="",
    client_ip="127.0.0.1",
    user_agent="Mozilla/5.0..."
)

# Get query statistics for a user
stats = QueryLog.get_query_stats(user_id="user-uuid", hours=24)
# Returns: (query_count, avg_time_ms, max_time_ms, total_rows, total_bytes, success_count, error_count)
```

Table Schema:
- `query_id` (String) - Unique query identifier
- `user_id` (UUID) - User who executed the query
- `query_text` (String) - SQL query text
- `query_type` (String) - Query type (SELECT, INSERT, etc.)
- `execution_time_ms` (UInt32) - Execution time in milliseconds
- `rows_read` (UInt64) - Number of rows read
- `bytes_read` (UInt64) - Number of bytes read
- `memory_used` (UInt64) - Memory used in bytes
- `status` (String) - Query status (success, error)
- `error_message` (String) - Error message if failed
- `timestamp` (DateTime64) - Query execution timestamp
- `client_ip` (String) - Client IP address
- `user_agent` (String) - Client user agent

#### Metrics Model

```python
from src.models.clickhouse import Metrics

# Initialize ClickHouse table (run once)
Metrics.create_table()

# Record a metric
Metrics.insert(
    metric_name="user.signups",
    metric_value=1.0,
    metric_type="counter",
    tags={"plan": "growth", "source": "organic"}
)

# Get average metric value
avg_value = Metrics.get_metric_avg(
    metric_name="user.signups",
    hours=24,
    tags={"plan": "growth"}
)

# Get sum of metric values
total_value = Metrics.get_metric_sum(
    metric_name="user.signups",
    hours=24,
    tags={"plan": "growth"}
)
```

Table Schema:
- `metric_id` (String) - Unique metric identifier
- `metric_name` (String) - Metric name
- `metric_value` (Float64) - Metric value
- `metric_type` (String) - Metric type (gauge, counter)
- `tags` (Map) - Key-value tags for filtering
- `timestamp` (DateTime64) - Metric timestamp

## Best Practices

### PostgreSQL

1. **Always use async sessions** - Use `get_db()` dependency or `get_db_context()` context manager
2. **Commit explicitly** - Sessions don't auto-commit, call `await db.commit()`
3. **Handle transactions** - Use try/except for proper transaction handling
4. **Use indexes wisely** - Create indexes on frequently queried columns
5. **Validate input** - Use Pydantic models for request/response validation
6. **Use migrations** - Never modify schema directly, use Alembic

### ClickHouse

1. **Batch inserts** - ClickHouse is optimized for bulk inserts
2. **Use appropriate engines** - MergeTree for time-series data
3. **Set TTL** - Automatically expire old data
4. **Partition by date** - Improve query performance
5. **Use materialized views** - Pre-compute aggregations

### Security

1. **Never log passwords** - Hash passwords before storage
2. **Use parameterized queries** - Prevent SQL injection
3. **Validate input** - Always validate user input
4. **Use environment variables** - Never hardcode credentials
5. **Rotate secrets** - Regularly update passwords and tokens

## Testing

### PostgreSQL

```python
import pytest
from httpx import AsyncClient
from src.database import init_db, close_db

@pytest.fixture
async def client():
    # Initialize test database
    await init_db()

    # Create test client
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    # Cleanup
    await close_db()
```

### ClickHouse

```python
from src.models.clickhouse import QueryLog

# Create test table
QueryLog.create_table()

# Insert test data
QueryLog.insert(
    query_id="test-query",
    user_id="test-user",
    query_text="SELECT 1",
    query_type="SELECT",
    execution_time_ms=10,
    rows_read=1,
    bytes_read=10,
    memory_used=100,
    status="success"
)

# Verify data
stats = QueryLog.get_query_stats(user_id="test-user", hours=1)
assert stats[0] == 1  # 1 query
```

## Troubleshooting

### Connection Issues

1. **Check environment variables** - Verify DATABASE_URL and CLICKHOUSE_URL
2. **Test connectivity** - Use `psql` and `clickhouse-client` to test connections
3. **Check logs** - Enable DB_ECHO for detailed SQL logging
4. **Verify permissions** - Ensure database user has required permissions

### Migration Issues

1. **Review migration** - Check auto-generated migration before applying
2. **Test locally** - Always test migrations on local database
3. **Rollback if needed** - Use `alembic downgrade -1` to rollback
4. **Stamp head** - Use `alembic stamp head` if tables already exist

### Performance Issues

1. **Add indexes** - Create indexes on frequently queried columns
2. **Use explain** - Use `EXPLAIN ANALYZE` to analyze query performance
3. **Optimize queries** - Avoid SELECT *, use specific columns
4. **Batch operations** - Use bulk inserts/updates for multiple records

## Next Steps

- [ ] Add more models as needed (e.g., Projects, Dashboards, Queries)
- [ ] Set up database backup strategy
- [ ] Configure connection pooling
- [ ] Add database monitoring
- [ ] Implement data retention policies
- [ ] Set up read replicas for PostgreSQL
- [ ] Configure ClickHouse replication
