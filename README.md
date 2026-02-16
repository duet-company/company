# AI Data Labs - Company Monorepo

**AI-First Data Infrastructure - Hours to Production, Not Months**

This is the official monorepo for Duet Company. It contains **ALL company code, documentation, and resources** in a unified repository.

## 🏗️ Complete Monorepo Structure

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
├── docs/                 # Complete documentation
│   ├── vision/           # Company vision, OKR, roadmap
│   ├── api/              # API documentation
│   ├── blog/             # Company blog content
│   ├── playbook/         # SOPs, playbooks, onboarding
│   └── users/            # User guides and tutorials
├── skills/               # OpenClaw AI agent skills
│   ├── company-skill.md
│   ├── github-skill.md
│   ├── project-skill.md
│   ├── marketing-skill.md
│   ├── sales-skill.md
│   ├── data-skill.md
│   ├── design-skill.md
│   ├── query-skill.md
│   ├── support-skill.md
│   └── ops-skill.md
├── kanboard/            # Task board and issue tracking
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

### Documentation

**Vision (docs/vision):**
- Company vision and mission
- OKRs (Objectives and Key Results)
- Roadmap (16-week execution plan)

**API (docs/api):**
- API reference documentation
- Endpoint specifications
- Authentication guide

**Blog (docs/blog):**
- Company blog content
- Technical articles
- AI and data engineering insights

**Playbook (docs/playbook):**
- Standard Operating Procedures (SOPs)
- Onboarding guides
- Incident response procedures

**Users (docs/users):**
- Getting started guides
- Tutorials
- Troubleshooting

### Skills (OpenClaw AI Agent Skills)

The monorepo includes 10 OpenClaw-compatible skills for automated operations:

**Company Operations:**
- `company-skill.md` - Sprint status, OKR progress, business metrics
- `github-skill.md` - Repository management, PRs, CI/CD
- `project-skill.md` - Task breakdown, milestone coordination

**Marketing & Sales:**
- `marketing-skill.md` - Content generation, campaigns
- `sales-skill.md` - Lead management, pipeline tracking

**Technical:**
- `data-skill.md` - Data engineering patterns
- `design-skill.md` - Infrastructure automation
- `query-skill.md` - Text-to-SQL with ClickHouse
- `support-skill.md` - Customer service with RAG
- `ops-skill.md` - Monitoring, CI/CD, incident response

### Kanboard

**Task Management:**
- Kanban board for project tracking
- Issue tracking
- Sprint management
- Task assignment

### Infrastructure

**Infrastructure as Code:**
- Terraform configurations
- Kubernetes manifests
- Helm charts
- CI/CD pipelines
- Monitoring stack

## 📚 Documentation

- **Architecture:** See `docs/api/architecture.md`
- **API Reference:** See `docs/api/`
- **Vision & Strategy:** See `docs/vision/`
- **Playbook:** See `docs/playbook/`
- **User Guides:** See `docs/users/`
- **Blog:** See `docs/blog/`
- **Skills Documentation:** See `skills/README.md`

## 🔗 External Repositories

**Only ONE active repository:**

- **company (this repo):** https://github.com/duet-company/company - Everything is here!

**All other repositories are archived:**
- vision → company/docs/vision
- docs → company/docs
- skills → company/skills
- blog → company/docs/blog
- playbook → company/docs/playbook
- kanban → company/kanboard
- kanboard → company/kanboard
- infrastructure → company/infrastructure
- backend → company/apps/backend
- frontend → company/apps/frontend
- platform → company (replaced)
- agent-* → company/agents/*

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
- **This Repo:** https://github.com/duet-company/company

---

**Last Updated:** February 16, 2026
**Maintained By:** duyetbot

**Note:** This monorepo contains ALL company code, documentation, and resources. No other active repositories needed!
