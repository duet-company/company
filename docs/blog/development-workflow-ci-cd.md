# Our Development Workflow: How We Ship Fast and Stay Sane

**Published:** February 21, 2026
**Reading Time:** 8 minutes
**Tags:** #devops #workflow #ci-cd #engineering #productivity

---

## TL;DR

At AI Data Labs, we've optimized our workflow for speed and reliability:

- **Feature branches** - Isolated development, easy reviews
- **Automated testing** - Catch bugs before they hit prod
- **CI/CD with GitHub Actions** - Deploy on merge, zero manual steps
- **Database migrations** - Version-controlled, backward-compatible
- **Staging environment** - Test before production
- **Monitoring-first** - Deployments include metrics and alerts
- **Rollback plan** - Always ready to revert

**Result:** Deploy to production in < 10 minutes, 99% success rate, zero manual steps.

---

## The Philosophy: Automate Everything

We believe in three principles:

1. **Automate repetitive tasks** - If you do it more than once, automate it
2. **Fail fast, fix fast** - Catch issues early, when they're cheap to fix
3. **Small, frequent releases** - Less risk, faster feedback

This philosophy drives our entire workflow.

---

## Git Workflow: Feature Branch Strategy

### Branch Structure

```
main (production)
  ↑
develop (staging)
  ↑
feature/query-optimization
feature/user-authentication
feature/dashboard-updates
bugfix/api-timeout
```

### Branch Naming Convention

- **Features:** `feature/<short-description>`
  - Example: `feature/query-caching`
- **Bug fixes:** `bugfix/<issue>`
  - Example: `bugfix/login-timeout`
- **Hot fixes:** `hotfix/<urgent-fix>`
  - Example: `hotfix/security-patch`
- **Releases:** `release/<version>`
  - Example: `release/v1.0.0`

### Workflow Steps

1. **Create branch:**
   ```bash
   git checkout -b feature/user-dashboard
   ```

2. **Develop and commit:**
   ```bash
   git add .
   git commit -m "feat: add user dashboard with analytics charts"
   ```

3. **Push and create PR:**
   ```bash
   git push origin feature/user-dashboard
   # Create PR on GitHub
   ```

4. **CI runs automatically:**
   - Linting (Biome, ESLint)
   - Type checking (TypeScript)
   - Unit tests (pytest, vitest)
   - Integration tests (test suite)

5. **Code review:**
   - Team reviews changes
   - At least 1 approval required
   - CI must pass

6. **Merge to develop:**
   - Triggers deployment to staging
   - Manual QA on staging environment

7. **Merge to main:**
   - Triggers deployment to production
   - Automated rollback on failure

### Commit Message Convention

We follow Conventional Commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(query): add result caching for 5 minute TTL

Reduces load on ClickHouse by 70% for repeated queries.

Closes #42
```

```
fix(auth): resolve token expiration bug

Tokens were expiring after 1 hour instead of 24 hours.

Fixes #38
```

---

## CI/CD Pipeline: GitHub Actions

### Pipeline Stages

```
┌─────────────────────────────────────────────────────────┐
│  Push to branch / Create PR                         │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │   Lint & Format        │
        │   (Biome, ESLint)      │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   Type Checking        │
        │   (TypeScript, mypy)   │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   Unit Tests          │
        │   (pytest, vitest)     │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   Integration Tests    │
        │   (test suite)         │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   Build Docker Images  │
        │   (push to GHCR)      │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   Deploy to Staging    │
        │   (if merge to develop) │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   Deploy to Production  │
        │   (if merge to main)    │
        └──────────────────────────┘
```

### GitHub Actions Workflow

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  # Job 1: Lint and format
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run lint
      - run: npm run format:check

  # Job 2: Type checking
  type-check:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run type-check

  # Job 3: Unit tests
  test:
    runs-on: ubuntu-latest
    needs: type-check
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run test:unit

  # Job 4: Integration tests
  test-integration:
    runs-on: ubuntu-latest
    needs: test
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
      clickhouse:
        image: clickhouse/clickhouse-server
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run test:integration

  # Job 5: Build and deploy to staging
  deploy-staging:
    runs-on: ubuntu-latest
    needs: test-integration
    if: github.ref == 'refs/heads/develop'
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker images
        run: |
          docker build -t ghcr.io/duet-company/fastapi:staging .
          docker push ghcr.io/duet-company/fastapi:staging
      - name: Deploy to staging
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.STAGING_HOST }}
          username: ${{ secrets.STAGING_USER }}
          key: ${{ secrets.STAGING_SSH_KEY }}
          script: |
            microk8s kubectl set image deployment/fastapi fastapi=ghcr.io/duet-company/fastapi:staging

  # Job 6: Build and deploy to production
  deploy-production:
    runs-on: ubuntu-latest
    needs: test-integration
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker images
        run: |
          docker build -t ghcr.io/duet-company/fastapi:${{ github.sha }} .
          docker push ghcr.io/duet-company/fastapi:${{ github.sha }}
      - name: Deploy to production
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            microk8s kubectl set image deployment/fastapi fastapi=ghcr.io/duet-company/fastapi:${{ github.sha }}
      - name: Health check
        run: |
          sleep 30  # Wait for deployment
          curl -f https://api.aidatalabs.ai/health || exit 1
```

### CI Metrics We Track

- **Pipeline duration:** < 5 minutes (fast feedback)
- **Test coverage:** > 80% target
- **Pass rate:** > 95% target
- **Deployment frequency:** Daily releases

---

## Testing Strategy

### Test Pyramid

```
        ┌─────────┐
        │  E2E    │  10 tests (slow, expensive)
        │ (5%)    │
        └────┬────┘
             │
    ┌────────▼─────┐
    │ Integration  │  50 tests (medium speed)
    │    (25%)     │
    └─────┬────────┘
          │
  ┌───────▼─────────┐
  │    Unit        │  200+ tests (fast, cheap)
  │    (70%)       │
  └────────────────┘
```

### Unit Tests

**What we test:**
- Business logic
- Data transformations
- Utility functions
- Algorithm correctness

**Example:**
```python
# tests/test_query_parser.py
import pytest
from src.query_parser import QueryParser

def test_parse_simple_query():
    parser = QueryParser()
    result = parser.parse("show me revenue by region")
    assert result.metric == "revenue"
    assert result.dimension == "region"
    assert result.time_range is None

def test_parse_query_with_time_range():
    parser = QueryParser()
    result = parser.parse("revenue over the past 7 days")
    assert result.metric == "revenue"
    assert result.time_range == "7d"

def test_parse_invalid_query():
    parser = QueryParser()
    with pytest.raises(InvalidQueryError):
        parser.parse("this is not a valid query")
```

### Integration Tests

**What we test:**
- API endpoints
- Database queries
- External integrations
- Service interactions

**Example:**
```python
# tests/test_api_integration.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_query_endpoint():
    response = client.post("/api/v1/query", json={
        "query": "show me revenue",
        "session_id": "test-session"
    })
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "execution_time_ms" in data

def test_query_with_invalid_input():
    response = client.post("/api/v1/query", json={
        "query": ""
    })
    assert response.status_code == 422  # Validation error
```

### End-to-End Tests

**What we test:**
- Critical user flows
- Multi-service interactions
- Real-world scenarios

**Example:**
```typescript
// tests/e2e/query-flow.test.ts
import { test, expect } from '@playwright/test';

test('user queries revenue and sees chart', async ({ page }) => {
  // Navigate to dashboard
  await page.goto('https://app.aidatalabs.ai');

  // Enter query
  await page.fill('input[name="query"]', 'show me revenue by region');

  // Submit
  await page.click('button[type="submit"]');

  // Wait for results
  await page.waitForSelector('.chart-container');

  // Verify chart is displayed
  const chart = page.locator('.chart-container');
  await expect(chart).toBeVisible();
});
```

---

## Database Migrations

### Version Control for Schema

We use Alembic for PostgreSQL migrations:

```bash
# Create migration
alembic revision --autogenerate -m "add users table"

# Review generated migration
# Edit if needed

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Migration File Example

```python
# alembic/versions/001_add_users_table.py
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()')),
    )
    op.create_index('idx_users_email', 'users', ['email'])

def downgrade():
    op.drop_index('idx_users_email', table_name='users')
    op.drop_table('users')
```

### ClickHouse Schema Changes

ClickHouse doesn't have traditional migrations, but we use versioning:

```sql
-- Version 1: Initial table
CREATE TABLE events_v1 (
    event_id UUID,
    user_id UUID,
    timestamp DateTime
) ENGINE = MergeTree()
ORDER BY (user_id, timestamp);

-- Version 2: Add new column (backwards compatible)
ALTER TABLE events_v1 ADD COLUMN event_type String DEFAULT 'unknown';

-- Version 3: Create new optimized table (migration path)
CREATE TABLE events_v2 (
    event_id UUID,
    user_id UInt64,
    timestamp DateTime64(3),
    event_type LowCardinality(String)
) ENGINE = MergeTree()
ORDER BY (user_id, timestamp);

-- Migrate data (can do gradually)
INSERT INTO events_v2 SELECT * FROM events_v1;

-- Switch over (instant)
RENAME TABLE events_v2 TO events, events TO events_old;
```

---

## Environments

### Local Development

- **Docker Compose** - All services locally
- **Hot reload** - Instant feedback
- **Shared dev database** - Consistent state

```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: aidatalabs_dev
    ports:
      - "5432:5432"

  clickhouse:
    image: clickhouse/clickhouse-server
    ports:
      - "8123:8123"

  fastapi:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://postgres@postgres/aidatalabs_dev
    volumes:
      - ./backend:/app
    command: uvicorn src.main:app --reload
```

### Staging Environment

- **Mirror of production** - Same stack, smaller scale
- **Manual QA** - Test before production
- **Analytics enabled** - Monitor staging performance

- **URL:** https://staging.aidatalabs.ai
- **Scale:** 1/2 of production resources

### Production Environment

- **High availability** - Multi-node (future)
- **Monitoring** - Full observability stack
- **Alerting** - Immediate notifications

- **URL:** https://aidatalabs.ai
- **Scale:** Full production resources

---

## Deployment Strategy

### Blue-Green Deployment

```
┌─────────────┐
│   Production │
│   (Blue)    │ ← Current version
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Staging    │ ← Deploy new version here
│   (Green)   │
└──────┬──────┘
       │
       │ Test passes
       ▼
┌─────────────┐
│   Production │
│   (Green)   │ ← Switch to new version
└─────────────┘
       │
       ▼
   (Blue) ← Keep for rollback
```

### Rollback Plan

Always ready to revert:

```bash
# Quick rollback to previous version
microk8s kubectl rollout undo deployment/fastapi

# Rollback to specific version
microk8s kubectl set image deployment/fastapi \
  fastapi=ghcr.io/duet-company/fastapi:<previous-sha>

# Health check after rollback
curl -f https://api.aidatalabs.ai/health
```

### Deployment Checklist

Before deploying to production:

- [ ] All tests pass
- [ ] Code review approved
- [ ] Staging verified
- [ ] Database migrations tested
- [ ] Rollback plan documented
- [ ] Monitoring dashboards updated
- [ ] On-call engineer notified

---

## Monitoring & Observability

### Metrics We Track

**Application:**
- Request rate (per minute)
- Error rate (per minute)
- Response time (P50, P95, P99)
- Database query time

**Infrastructure:**
- CPU usage (%)
- Memory usage (%)
- Disk I/O
- Network traffic

**Business:**
- Active users
- Queries per user
- Revenue generated
- Error types

### Alerts

```yaml
# Prometheus alerts
groups:
  - name: production
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        annotations:
          summary: "Error rate exceeds 5%"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 1
        annotations:
          summary: "P95 response time exceeds 1s"

      - alert: DeploymentFailure
        expr: deployment_failed == 1
        annotations:
          summary: "Deployment to production failed"
```

---

## Best Practices We Follow

### 1. Small, Frequent Commits

**Bad:**
- One giant commit with 50 files
- Diff is impossible to review
- Rollback is all-or-nothing

**Good:**
- Multiple small commits, each focused
- Easy to review each change
- Can revert individual commits

### 2. Tests Before Code

**TDD approach:**
1. Write failing test
2. Write code to make test pass
3. Refactor

**Benefits:**
- Tests guide design
- Guarantees code works
- Catches regressions early

### 3. Documentation as Code

We document in code, not separately:

```python
def generate_clickhouse_sql(parsed_query: ParsedQuery) -> str:
    """
    Generate optimized ClickHouse SQL from parsed natural language query.

    Args:
        parsed_query: Parsed query with metric, dimension, time_range

    Returns:
        ClickHouse SQL query string

    Example:
        >>> generate_clickhouse_sql(ParsedQuery(
        ...     metric="revenue",
        ...     dimension="region"
        ... ))
        "SELECT region, sum(revenue) FROM events GROUP BY region"
    """
    ...
```

### 4. Code Reviews are Mandatory

Every change goes through review:
- Catch bugs early
- Share knowledge
- Improve code quality
- Mentorship opportunity

### 5. Automate Boring Stuff

- Formatting: Biome, Prettier
- Type checking: TypeScript, mypy
- Testing: pytest, vitest
- Deployment: GitHub Actions

---

## Tools We Use

| Purpose | Tool | Why? |
|----------|-------|-------|
| Version control | Git | Industry standard |
| CI/CD | GitHub Actions | Free, integrated with GitHub |
| Code quality | Biome, ESLint | Fast, modern linters |
| Type checking | TypeScript, mypy | Catch errors at compile time |
| Testing | pytest, vitest, Playwright | Comprehensive test stack |
| Docker | Docker, Docker Compose | Containerization |
| Database migrations | Alembic | Python, mature ecosystem |
| Monitoring | Prometheus + Grafana | Industry standard |
| Documentation | Markdown, Sphinx | Simple, version-controlled |

---

## Lessons Learned

### 1. Speed Matters

Fast CI/CD means:
- Faster feedback
- Faster fixes
- Happier developers

Our goal: < 5 minutes from push to green.

### 2. Tests Save Time

Writing tests takes time up front, but saves hours later:
- Catch bugs before production
- Prevent regressions
- Enable refactoring with confidence

### 3. Automate or Die

Manual deployments are a liability:
- Human error
- Inconsistent process
- Slow feedback loop

Automate everything.

### 4. Monitor Everything

Without monitoring, you're flying blind:
- Don't know if deployment succeeded
- Don't know if something broke
- Can't troubleshoot issues

### 5. Keep It Simple

Don't over-engineer:
- Start simple
- Add complexity when needed
- Remove complexity when not needed

---

## Conclusion

Our workflow isn't revolutionary. It's just doing the basics well:

- Feature branches for isolation
- Automated testing for reliability
- CI/CD for speed
- Monitoring for visibility

The result:
- Deploy to production in < 10 minutes
- 99% deployment success rate
- Zero manual steps
- Happy team, happy users

Ship fast, ship often, ship confidently.

---

**Want to learn more?**

- Check our [tech stack](/blog/tech-stack-architecture)
- See our [open source code](https://github.com/duet-company)
- Follow us on Twitter [@duetcompany](https://twitter.com/duetcompany)

**Questions?** Say hi at [hello@aidatalabs.ai](mailto:hello@aidatalabs.ai)

---

*This post is part 1 of our Engineering Culture Series. Next up: "On-Call at a Startup: How We Handle Production Incidents."*
