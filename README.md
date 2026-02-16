# AI Data Labs - Company Monorepo

**AI-First Data Infrastructure - Hours to Production, Not Months**

This is the official monorepo for Duet Company's AI Data Labs platform. It contains all company code including frontend, backend, AI agents, infrastructure, and documentation in a unified repository.

## 🏗️ Monorepo Structure

```
company/
├── apps/                    # Applications
│   ├── frontend/          # React + TypeScript web dashboard
│   ├── backend/           # FastAPI backend service
│   └── api/               # API gateway and endpoints
├── packages/              # Shared packages
│   ├── shared/           # Shared utilities and helpers
│   ├── types/            # TypeScript type definitions
│   └── config/           # Shared configuration
├── agents/               # AI agents
│   ├── query/            # Query Agent (NL to SQL)
│   ├── design/           # Design Agent (infrastructure automation)
│   └── support/          # Support Agent (24/7 assistance)
├── docs/                # Documentation
├── infrastructure/      # Infrastructure as Code
├── scripts/             # Build and automation scripts
└── [monorepo config files]
```

## 🚀 Quick Start

### Prerequisites

- **bun:** `curl -fsSL https://bun.sh/install | bash`
- **Python 3.11+:** For backend services
- **Kubernetes:** `microk8s install` (or use cloud K8s)

### Installation

```bash
# Clone the repository
git clone https://github.com/duet-company/company.git
cd company

# Install all dependencies (bun workspaces)
bun install
```

### Development

```bash
# Start all services in dev mode
bun run dev

# Start specific app
bun run --filter @duet-company/frontend dev
bun run --filter @duet-company/backend dev

# Run tests
bun run test

# Lint and format
bun run lint
bun run format

# Type check
bun run typecheck

# Build all packages
bun run build
```

## 📦 Technology Stack

### Core Tools
- **bun:** JavaScript runtime and package manager (10x faster than npm)
- **biome:** Linter + formatter (100x faster than ESLint/Prettier)
- **TypeScript:** Strict mode for type safety

### Applications

**Frontend (apps/frontend):**
- Next.js 14 with App Router
- React 18 + TypeScript
- Tailwind CSS
- TanStack Query

**Backend (apps/backend):**
- FastAPI (Python 3.11+)
- Pydantic for validation
- ClickHouse client
- PostgreSQL client

**API (apps/api):**
- API Gateway
- Authentication middleware
- Rate limiting
- Request routing

### Packages

**Shared (packages/shared):**
- Utility functions
- Shared constants
- Common helpers

**Types (packages/types):**
- TypeScript type definitions
- API schemas
- Data models

**Config (packages/config):**
- Environment configuration
- CI/CD configs
- Build configs

### AI Agents

**Query Agent (agents/query):**
- Natural language to SQL translation
- ClickHouse query optimization
- Query result caching

**Design Agent (agents/design):**
- Infrastructure automation
- Schema design
- K8s manifest generation

**Support Agent (agents/support):**
- RAG-based knowledge base
- 24/7 customer assistance
- Ticket routing

## 🔗 Related Repositories

- **Company Website:** https://aidatalabs.ai (deployed from Cloudflare Workers)
- **Documentation:** https://docs.aidatalabs.ai (deployed from `docs/` folder)
- **Skills Repository:** https://github.com/duet-company/skills (OpenClaw skills)
- **Vision & Strategy:** https://github.com/duet-company/vision (OKRs, roadmap)

## 📊 Workspaces

This monorepo uses **bun workspaces** for efficient dependency management:

```json
{
  "workspaces": [
    "apps/*",
    "packages/*",
    "agents/*"
  ]
}
```

### Workspace Benefits

- **Single node_modules:** Faster installs, less disk space
- **Hoisting:** Shared dependencies installed at root
- **Linked packages:** Local packages can import each other
- **Selective commands:** Run scripts in specific workspaces

### Workspace Commands

```bash
# Install dependencies for specific workspace
bun install --filter @duet-company/frontend

# Run script in specific workspace
bun run --filter @duet-company/backend test

# Run script in all workspaces matching pattern
bun run --filter '*build*' build
```

## 🛠️ Development Workflow

### Code Style

We use **biome** for linting and formatting:

```bash
# Check code
bun run lint

# Auto-fix issues
bun run lint:fix

# Format code
bun run format
```

### Type Safety

All TypeScript code uses strict mode:

```bash
# Type check all workspaces
bun run typecheck
```

### Testing

```bash
# Run all tests
bun run test

# Run tests for specific workspace
bun run --filter @duet-company/frontend test
```

## 🚢 Deployment

### Frontend
- **Build:** `bun run --filter @duet-company/frontend build`
- **Deploy:** Cloudflare Workers (static site)
- **URL:** https://aidatalabs.ai

### Backend
- **Build:** Docker image built from `apps/backend/Dockerfile`
- **Deploy:** Kubernetes (microk8s)
- **Health Check:** `/health` endpoint

### Infrastructure
- **Terraform:** `cd infrastructure && terraform apply`
- **K8s Manifests:** `kubectl apply -f k8s/`
- **Monitoring:** Prometheus + Grafana

## 📝 Documentation

- **Architecture:** See `docs/architecture.md`
- **API Reference:** See `docs/api.md`
- **Contributing:** See `docs/contributing.md`
- **Development Guide:** See `docs/development.md`

## 🔒 Security

- **Secrets:** Stored in GitHub Secrets (not committed)
- **Environment:** `.env.example` for reference
- **Access:** All repos are public, internal tools are private
- **Scanning:** GitHub Secret Scanning enabled

## 📈 Performance Targets

- **Frontend Build:** < 30 seconds (bun)
- **API Response:** < 200ms (95th percentile)
- **Query Time:** < 1 second (95th percentile, ClickHouse)
- **Cold Start:** < 100ms (Workers AI)
- **Uptime:** 99.9%+ (3 nines)

## 🤝 Contributing

1. Fork this repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and commit: `git commit -m 'feat: add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Commit Conventions

We use conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `test:` Test additions/changes
- `chore:` Maintenance tasks

## 📄 License

MIT License - See [LICENSE](LICENSE) file

## 🏢 Organization

**Duet Company** - AI Data Labs
- **Website:** https://aidatalabs.ai
- **GitHub:** https://github.com/duet-company
- **Blog:** https://blog.aidatalabs.ai

---

**Last Updated:** February 16, 2026
**Maintained By:** duyetbot
