# Security First: How We Protect AI Data Labs

**Published:** February 21, 2026
**Reading Time:** 10 minutes
**Tags:** #security #engineering #compliance #infrastructure

---

## TL;DR

Security isn't an afterthought at AI Data Labs—it's foundational. Our security posture:

- **Defense in depth** - Multiple layers of protection
- **Zero trust** - Verify everything, trust nothing
- **Encryption everywhere** - Data encrypted at rest and in transit
- **Least privilege** - Minimal access, just-in-time permissions
- **Automated security** - Security as code, continuous scanning
- **Compliance ready** - GDPR, SOC 2 framework

**Result:** Production-grade security for a $74/month infrastructure.

---

## Our Security Philosophy

### Three Core Principles

1. **Security is everyone's job** - Not just a security team's problem
2. **Secure by design** - Built in from day one, not bolted on later
3. **Transparency** - Security practices are documented and auditable

### Defense in Depth

We assume layers will fail. We build multiple layers:

```
┌─────────────────────────────────────────┐
│     Layer 1: Network Security         │
│   Cloudflare WAF, DDoS protection    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│     Layer 2: Application Security      │
│   HTTPS, input validation, rate limiting│
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│     Layer 3: Authentication         │
│   MFA, JWT tokens, session management│
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│     Layer 4: Authorization          │
│   RBAC, least privilege, audit logs   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│     Layer 5: Data Security         │
│   Encryption at rest and in transit   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│     Layer 6: Infrastructure        │
│   Firewall, secure configs, updates   │
└───────────────────────────────────────┘
```

---

## Network Security

### Layer 1: Cloudflare WAF & DDoS Protection

**What it protects:**
- DDoS attacks (volumetric, protocol, application layer)
- SQL injection
- XSS attacks
- Path traversal
- Bot attacks

**Configuration:**
```yaml
# Cloudflare WAF rules
rules:
  - name: Block SQL injection
    expression: http.request.body contains "UNION SELECT"
    action: block

  - name: Rate limit API
    expression: http.request.uri.path matches "^/api/.*"
    action: ratelimit
    ratelimit:
      requests_per_minute: 100
      period: 60
```

**Benefits:**
- Stops attacks at edge (never reach our servers)
- Free with Cloudflare Pro ($20/month)
- Real-time threat intelligence
- Zero configuration needed

### Layer 6: Firewall Rules

**DigitalOcean Cloud Firewall:**

```yaml
# Only allow necessary traffic
inbound:
  - port: 22
    protocol: tcp
    sources:
      - trusted-vpn-ip/32  # SSH from VPN only

  - port: 80
    protocol: tcp
    sources: 0.0.0.0/0  # HTTP (redirects to HTTPS)

  - port: 443
    protocol: tcp
    sources: 0.0.0.0/0  # HTTPS

  - port: 6443
    protocol: tcp
    sources: 10.0.0.0/8  # Kubernetes API (internal only)

outbound:
  - protocol: any
    destinations: 0.0.0.0/0  # Allow all outbound
```

**Benefits:**
- Minimal attack surface
- No public SSH access
- Internal services isolated

---

## Application Security

### HTTPS/TLS Everywhere

**No plaintext, ever:**

```nginx
# NGINX configuration
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;

    # Modern TLS configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # HSTS (force HTTPS)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # OCSP stapling
    ssl_stapling on;
    ssl_stapling_verify on;

    # Redirect HTTP to HTTPS
    error_page 497 301 =307 https://$host:$server_port$request_uri;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    return 301 https://$host$request_uri;
}
```

**Certificates:**
- Let's Encrypt via Cloudflare (free, auto-renew)
- Automatic certificate renewal
- Full SSL chain

### Input Validation

**Never trust user input:**

```python
from pydantic import BaseModel, validator, constr
from typing import Optional

class QueryRequest(BaseModel):
    query: constr(max_length=1000)  # Limit query length
    session_id: Optional[str]

    @validator('query')
    def validate_query(cls, v):
        # Check for SQL injection patterns
        dangerous_patterns = [
            'UNION', 'DROP', 'DELETE', 'TRUNCATE',
            'INSERT', 'UPDATE', 'ALTER', '--', ';'
        ]
        v_upper = v.upper()
        for pattern in dangerous_patterns:
            if pattern in v_upper:
                raise ValueError('Query contains forbidden keywords')
        return v

    @validator('session_id')
    def validate_session(cls, v):
        if v and not v.isalnum():
            raise ValueError('Invalid session ID format')
        return v
```

### Rate Limiting

**Prevent abuse:**

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute", "1000/hour"]
)

@app.post("/api/v1/query")
@limiter.limit("50/minute")  # Stricter limit for expensive queries
async def execute_query(request: Request, data: QueryRequest):
    ...
```

---

## Authentication & Authorization

### Authentication: JWT + MFA

**Token-based authentication:**

```python
from datetime import datetime, timedelta
import jwt

def create_access_token(user_id: str) -> str:
    """Create JWT access token"""
    payload = {
        'sub': user_id,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=1),
        'type': 'access'
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token: str) -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")
```

**MFA for admin accounts:**

```python
import pyotp

def enable_mfa(user_id: str):
    """Enable MFA for user"""
    secret = pyotp.random_base32()
    # Store secret encrypted in database
    user.mfa_secret = encrypt(secret)
    # Show QR code for user to scan
    qr_code = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user.email,
        issuer_name="AI Data Labs"
    )
    return qr_code

def verify_mfa(user_id: str, code: str) -> bool:
    """Verify MFA code"""
    user = get_user(user_id)
    totp = pyotp.TOTP(decrypt(user.mfa_secret))
    return totp.verify(code)
```

### Authorization: RBAC

**Role-based access control:**

```python
from enum import Enum

class Role(str, Enum):
    USER = "user"
    ANALYST = "analyst"
    ADMIN = "admin"

class Permission(str, Enum):
    QUERY_DATA = "query:data"
    CREATE_DASHBOARD = "create:dashboard"
    MANAGE_USERS = "manage:users"
    VIEW_LOGS = "view:logs"

# Role to permissions mapping
ROLE_PERMISSIONS = {
    Role.USER: [Permission.QUERY_DATA],
    Role.ANALYST: [
        Permission.QUERY_DATA,
        Permission.CREATE_DASHBOARD
    ],
    Role.ADMIN: [
        Permission.QUERY_DATA,
        Permission.CREATE_DASHBOARD,
        Permission.MANAGE_USERS,
        Permission.VIEW_LOGS
    ]
}

def has_permission(user_role: Role, required_permission: Permission) -> bool:
    """Check if user has required permission"""
    return required_permission in ROLE_PERMISSIONS.get(user_role, [])
```

**Usage in API:**

```python
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> User:
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = verify_token(token)
    user = get_user(payload['sub'])
    return user

async def require_permission(permission: Permission):
    """Require specific permission"""
    async def check_permission(
        user: User = Depends(get_current_user)
    ):
        if not has_permission(user.role, permission):
            raise HTTPException(403, "Insufficient permissions")
        return user
    return check_permission

@app.post("/api/v1/query")
async def execute_query(
    request: QueryRequest,
    user: User = Depends(require_permission(Permission.QUERY_DATA))
):
    # User has permission to query
    ...
```

---

## Data Security

### Encryption at Rest

**Full disk encryption:**

```bash
# LUKS encryption on DigitalOcean droplet
cryptsetup luksFormat /dev/sdb
cryptsetup luksOpen /dev/sdb encrypted_disk
```

**Database encryption:**

```sql
-- ClickHouse data encryption
<clickhouse>
    <encryption>
        <disk>
            <path>/var/lib/clickhouse/disks/encrypted</path>
            <key>my-secret-key</key>
        </disk>
    </encryption>
</clickhouse>
```

**PostgreSQL encryption:**

```sql
-- Transparent Data Encryption (TDE)
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = '/var/lib/postgresql/server.crt';
ALTER SYSTEM SET ssl_key_file = '/var/lib/postgresql/server.key';
```

### Encryption in Transit

**All connections use TLS:**

```python
# ClickHouse connection
from clickhouse_connect import get_client

client = get_client(
    host='clickhouse.aidatalabs.ai',
    port=8443,
    username='default',
    password='',
    secure=True,  # Use HTTPS
    verify=True  # Verify SSL certificate
)

# PostgreSQL connection
import psycopg2

conn = psycopg2.connect(
    host='postgres.aidatalabs.ai',
    port=5432,
    dbname='aidatalabs',
    user='postgres',
    password='password',
    sslmode='require'  # Require SSL
)
```

### Secrets Management

**Never commit secrets to Git:**

```bash
# .gitignore
secrets/
*.key
*.pem
.env
terraform.tfvars
```

**Use Kubernetes secrets:**

```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: aidatalabs-secrets
type: Opaque
data:
  database-password: <base64-encoded-password>
  jwt-secret: <base64-encoded-jwt-secret>
  api-key: <base64-encoded-api-key>
```

**Use environment variables:**

```python
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str = Field(..., env='DATABASE_URL')
    jwt_secret: str = Field(..., env='JWT_SECRET')
    api_key: str = Field(..., env='API_KEY')

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Security Automation

### Dependency Scanning

**Automated vulnerability scanning:**

```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on: [push, pull_request]

jobs:
  vulnerability-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
```

### Container Scanning

**Scan Docker images for vulnerabilities:**

```bash
# Scan image
docker scan ghcr.io/duet-company/fastapi:latest

# Scan in CI
- name: Docker vulnerability scan
  run: |
    docker build -t temp-image .
    trivy image --severity HIGH,CRITICAL temp-image
```

### Infrastructure as Code Security

**Check Terraform for security issues:**

```bash
# tfsec - Security scanner for Terraform
pip install tfsec

tfsec ./terraform/

# Output:
✗ Security check violation
  Resource: aws_db_instance.main
  ID: AUR009
  Message: DB instance encryption is not enabled

  Path: main.tf:45-50
  ...
```

### Code Scanning (SAST)

**Static application security testing:**

```yaml
- name: Run Snyk security scan
  run: |
    npm install -g snyk
    snyk auth ${{ secrets.SNYK_TOKEN }}
    snyk test --json > snyk-results.json
```

---

## Auditing & Monitoring

### Comprehensive Audit Logs

**Log everything security-relevant:**

```python
import structlog

logger = structlog.get_logger()

async def log_security_event(
    event_type: str,
    user_id: str,
    details: dict,
    severity: str = "info"
):
    """Log security event"""
    logger.info(
        "security_event",
        event_type=event_type,
        user_id=user_id,
        details=details,
        severity=severity,
        timestamp=datetime.utcnow().isoformat()
    )

# Usage
await log_security_event(
    event_type="login",
    user_id="user-123",
    details={
        "ip": request.client.host,
        "user_agent": request.headers["user-agent"],
        "mfa_verified": True
    }
)

await log_security_event(
    event_type="query_execution",
    user_id="user-123",
    details={
        "query": "SELECT * FROM events",
        "execution_time_ms": 150
    },
    severity="info"
)

await log_security_event(
    event_type="failed_login",
    user_id="user-123",
    details={
        "ip": request.client.host,
        "reason": "invalid_password"
    },
    severity="warning"
)
```

### Security Metrics

**Track security KPIs:**

```yaml
# Prometheus security metrics
security_failed_logins_total
security_successful_logins_total
security_mfa_failures_total
security_blocked_requests_total
security_vulnerabilities_detected

# Alerts
- alert: HighFailedLogins
  expr: rate(security_failed_logins_total[5m]) > 10
  annotations:
    summary: "High rate of failed logins - possible attack"

- alert: VulnerabilityDetected
  expr: security_vulnerabilities_detected > 0
  annotations:
    summary: "New security vulnerabilities detected"
```

---

## Incident Response

### Security Incident Playbook

**Pre-defined procedures:**

```markdown
# Security Incident Response Plan

## Severity Levels

- **P1 (Critical)** - Data breach, active attack
- **P2 (High)** - Potential breach, suspicious activity
- **P3 (Medium)** - Vulnerability discovered, no exploit
- **P4 (Low)** - Minor security issue

## Response Procedures

### P1 - Critical Response (within 15 minutes)

1. **Contain**
   - Shut down affected services
   - Revoke compromised credentials
   - Block malicious IPs

2. **Assess**
   - Identify attack vector
   - Determine data impact
   - Preserve logs and evidence

3. **Remediate**
   - Patch vulnerabilities
   - Restore from clean backups
   - Strengthen defenses

4. **Communicate**
   - Notify affected customers
   - Update security incident page
   - Coordinate with law enforcement (if needed)

### P2 - High Response (within 1 hour)

[Similar steps, but less urgent]

### P3 - Medium Response (within 24 hours)

- Schedule fix
- Monitor for exploits
- Communicate timeline to stakeholders

### P4 - Low Response (within 1 week)

- Include in backlog
- Fix in next sprint
- Document for future reference
```

---

## Compliance

### GDPR Compliance

**Data protection measures:**

1. **Data minimization** - Only collect what's needed
2. **Right to be forgotten** - Delete user data on request
3. **Data portability** - Export user data on request
4. **Consent management** - Explicit consent for data processing
5. **Data breach notification** - 72-hour notification requirement

### SOC 2 Framework

**Security controls:**

1. **Access control** - MFA, RBAC, least privilege
2. **Change management** - Code review, audit trails
3. **Incident response** - Documented procedures, tested regularly
4. **Monitoring** - Real-time alerts, logging
5. **Vendor management** - Assess third-party security

---

## Best Practices We Follow

### 1. Never Trust User Input

Always validate, sanitize, and parameterize:
```python
# Bad
sql = f"SELECT * FROM users WHERE id = {user_id}"

# Good
sql = "SELECT * FROM users WHERE id = %(user_id)s"
cursor.execute(sql, {"user_id": user_id})
```

### 2. Use Prepared Statements

Prevent SQL injection:
```python
# ClickHouse prepared statement
query = "SELECT * FROM events WHERE user_id = %(user_id)s"
result = client.query(query, parameters={"user_id": user_id})
```

### 3. Keep Dependencies Updated

Automated dependency updates:
```yaml
# .github/workflows/dependency-update.yml
name: Dependency Update
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  workflow_dispatch:
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
      - run: |
          pip install pip-tools
          pip-compile requirements.in
          pip-sync
      - run: git commit -am "Update dependencies"
      - uses: ad-m/github-push-action@master
```

### 4. Regular Security Audits

- Monthly penetration testing
- Quarterly security reviews
- Annual independent audit
- Continuous vulnerability scanning

### 5. Security Training

- All team members complete security training
- Phishing simulations monthly
- Incident response drills quarterly

---

## Lessons Learned

### 1. Security is a Process, Not a Product

You can't buy security. You build it continuously.

### 2. Assume Breach

Design for "when" not "if". Containment matters.

### 3. Defense in Depth Works

Multiple layers. If one fails, others protect.

### 4. Automation is Essential

Manual security doesn't scale. Automate everything.

### 5. Transparency Builds Trust

Be open about security practices and incidents.

---

## Quick Security Checklist

Use this checklist for your project:

**Network Security:**
- [ ] WAF enabled (Cloudflare)
- [ ] DDoS protection
- [ ] Firewall rules (minimum attack surface)
- [ ] SSH restricted to VPN
- [ ] HTTPS/TLS everywhere

**Application Security:**
- [ ] Input validation
- [ ] Rate limiting
- [ ] XSS protection
- [ ] CSRF protection
- [ ] Secure headers (HSTS, CSP)

**Authentication & Authorization:**
- [ ] JWT token-based auth
- [ ] MFA for sensitive operations
- [ ] RBAC implemented
- [ ] Secure session management
- [ ] Password hashing (bcrypt/argon2)

**Data Security:**
- [ ] Encryption at rest
- [ ] Encryption in transit
- [ ] Secrets management (never in code)
- [ ] Data minimization
- [ ] Backup and recovery plan

**Monitoring:**
- [ ] Comprehensive logging
- [ ] Security metrics
- [ ] Real-time alerts
- [ ] Incident response plan
- [ ] Regular security audits

---

## Conclusion

Security isn't optional. It's essential.

At AI Data Labs, security is built into everything we do:
- Multiple defense layers
- Automated scanning and monitoring
- Comprehensive audit logging
- Incident response procedures
- Compliance readiness

You don't need a big budget. You need to be intentional.

Security first, always.

---

**Want to learn more?**

- Check our [tech stack](/blog/tech-stack-architecture)
- Learn about our [CI/CD security](/blog/development-workflow-ci-cd)
- Follow us on Twitter [@duetcompany](https://twitter.com/duetcompany)

**Questions?** Say hi at [hello@aidatalabs.ai](mailto:hello@aidatalabs.ai)

---

*This post is part 1 of our Security Series. Next up: "Incident Response: How We Handle Security Breaches."*
