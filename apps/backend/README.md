# AI Data Labs - Backend

FastAPI backend service for AI Data Labs platform.

## 🚀 Getting Started

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## 📁 Structure

```
src/
├── main.py           # FastAPI application entry point
├── api/              # API routes
├── models/           # Pydantic models
├── services/         # Business logic
└── config/           # Configuration
```

## 🛠️ Tech Stack

- **Framework:** FastAPI
- **Language:** Python 3.11+
- **Validation:** Pydantic
- **Database:** ClickHouse, PostgreSQL
- **Testing:** pytest

## 🔗 Links

- **Frontend:** https://github.com/duet-company/company/tree/main/apps/frontend
- **Platform:** https://github.com/duet-company/company
- **Docs:** https://docs.aidatalabs.ai
