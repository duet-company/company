# AI Data Labs - Authentication System

Complete JWT-based authentication system for the AI Data Labs platform.

## Features

- ✅ User registration and login
- ✅ JWT access tokens (30 min expiry)
- ✅ JWT refresh tokens (7 day expiry)
- ✅ Password hashing with bcrypt
- ✅ Role-based access control (admin, user, guest)
- ✅ Protected route middleware
- ✅ In-memory user storage (replace with PostgreSQL in production)
- ✅ Default admin user initialization

## API Endpoints

### Authentication (`/api/v1/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/register` | Register new user | No |
| POST | `/login` | Login with email/password | No |
| POST | `/refresh` | Refresh access token | No |
| GET | `/me` | Get current user info | Yes |
| POST | `/init-admin` | Initialize default admin | No |

## Default Admin User

After first startup, a default admin user is created:

- **Email:** `admin@aidatalabs.ai`
- **Password:** `admin123`
- **Role:** Admin

⚠️ **IMPORTANT:** Change the default admin password in production!

## Usage Examples

### Register a User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b...",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "user",
    "is_active": true
  }
}
```

### Access Protected Route

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

### Refresh Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
  }'
```

## Project Structure

```
src/
├── api/
│   └── v1/
│       └── auth.py          # Authentication endpoints
├── auth/
│   ├── security.py           # JWT & password hashing
│   └── service.py            # User management service
├── models/
│   └── user.py               # User data models
├── schemas/
│   └── auth.py               # API request/response schemas
└── main.py                   # FastAPI app entry point
```

## Security Features

- **Password Hashing:** Using bcrypt with passlib
- **JWT Tokens:** Signed with HS256 algorithm
- **Token Expiry:** Access tokens (30min), Refresh tokens (7 days)
- **CORS:** Configured for cross-origin requests
- **Role-Based Access Control:** Admin, User, Guest roles
- **Global Exception Handler:** Prevents information leakage

## Configuration

Environment variables (create `.env` file):

```bash
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## Next Steps

- [ ] Replace in-memory storage with PostgreSQL
- [ ] Add email verification for registration
- [ ] Implement password reset flow
- [ ] Add rate limiting for auth endpoints
- [ ] Implement 2FA/MFA support
- [ ] Add audit logging
- [ ] Configure CORS for production domains

## Dependencies

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `pyjwt` - JWT token handling
- `passlib` - Password hashing
- `python-multipart` - Form data parsing

## Development

Run the API:

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
cd apps/backend
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Access interactive API docs at: `http://localhost:8000/api/docs`

## Testing

Test authentication flow:

```bash
# 1. Initialize admin
curl -X POST "http://localhost:8000/api/v1/auth/init-admin"

# 2. Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@aidatalabs.ai", "password": "admin123"}'

# 3. Get user info
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## License

Copyright © 2026 Duet Company. All rights reserved.
