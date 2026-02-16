# Technology Stack

Complete technology stack for Duet Company's AI Data Labs platform.

## Core Philosophy

- **Speed to Value:** Use fast, modern tooling (bun, biome, Rust)
- **Developer Experience:** Type safety, great DX, minimal friction
- **Production Ready:** Cloud-native, scalable, observable
- **Open Source:** No vendor lock-in, community-driven

## Languages & Runtimes

### TypeScript
- **Use:** Frontend (React/Next.js), Backend API (FastAPI type hints)
- **Strict Mode:** Enabled for maximum type safety
- **Benefits:** Catch errors at compile-time, better IDE support

### Rust
- **Use:** Performance-critical components (data ingestion, query optimization)
- **Why:** Zero-cost abstractions, memory safety, blazing fast
- **Future Plans:** Custom ClickHouse UDFs, streaming data processors

### Python
- **Use:** Backend API (FastAPI), data processing, ML models
- **Why:** Rich ecosystem (pandas, numpy, scikit-learn), easy to learn

### bun (JavaScript Runtime)
- **Use:** Frontend build tool, package manager, test runner
- **Why:** 10x faster than npm, drop-in Node.js replacement, built-in TypeScript
- **Replaces:** npm, yarn, pnpm, webpack, jest

## Build & Developer Tools

### biome (Linter + Formatter)
- **Use:** Code quality, formatting, consistent style
- **Why:** 100x faster than ESLint/Prettier, single tool, better errors
- **Replaces:** ESLint, Prettier, Prettier-ESLint
- **Config:** Biome shares config with ESLint/Prettier for easy migration

### Next.js 14
- **Use:** Frontend framework, SSR/SSG, API routes
- **Why:** App Router, Server Components, excellent DX
- **Features:**
  - Server-Side Rendering (SSR)
  - Static Site Generation (SSG)
  - API routes
  - Image optimization
  - Font optimization

## Databases & Storage

### ClickHouse
- **Use:** Analytics database, time-series data, real-time queries
- **Why:** Columnar storage, 300% better compression, 2x-100x faster queries
- **Deployment:** Kubernetes (multi-replica cluster)

### PostgreSQL
- **Use:** Metadata storage, user data, configuration
- **Why:** Reliability, ACID compliance, rich ecosystem

### Apache Kafka
- **Use:** Event streaming, real-time data pipelines
- **Why:** High throughput, durability, scalability

## Orchestration & Deployment

### Kubernetes (microk8s)
- **Use:** Container orchestration, service management
- **Why:** Cloud-native, self-healing, auto-scaling

### Cloudflare Workers
- **Use:** Website deployment (static site rendering)
- **Why:** Global edge deployment, fast everywhere, free tier
- **Features:**
  - Static site generation
  - Global CDN
  - Automatic HTTPS
  - DDoS protection

### Terraform
- **Use:** Infrastructure as Code (IaC)
- **Why:** Version-controlled infrastructure, reproducible deployments

## AI/LLM

### Multi-Provider Strategy
We use a multi-provider approach for reliability and cost optimization:

#### Workers AI (Cloudflare)
- **Use:** Primary AI inference (serverless, low latency)
- **Why:** Built-in to Cloudflare, no cold starts, pay-as-you-go
- **Models:** Llama 2, Mistral, etc.

#### OpenRouter
- **Use:** Fallback and advanced models
- **Why:** Single API for multiple providers, competitive pricing
- **Models:** Claude, GPT-4, GLM-5, Claude 3.5 Sonnet

#### Fallback Strategy
1. Primary: Workers AI (fastest, lowest latency)
2. Fallback: OpenRouter (reliability, model variety)
3. Auto-switch based on cost/performance needs

### AI Agents
- **Query Agent:** Natural language to SQL (ClickHouse)
- **Design Agent:** Infrastructure automation
- **Support Agent:** 24/7 customer assistance (RAG-based)

## Frontend Stack

### React 18
- **Use:** UI framework
- **Features:** Hooks, Context, Suspense

### TypeScript
- **Use:** Type-safe React components
- **Benefits:** Better DX, fewer runtime errors

### Tailwind CSS
- **Use:** Utility-first CSS framework
- **Why:** Rapid development, small bundle size, easy customization

### TanStack Query (React Query)
- **Use:** Data fetching, caching, synchronization
- **Why:** Automatic caching, background updates, optimistic updates

### Axios
- **Use:** HTTP client
- **Why:** Promise-based, interceptors, request cancellation

## Backend Stack

### FastAPI (Python)
- **Use:** Backend API
- **Why:** Fast, async support, automatic OpenAPI docs, type hints
- **Features:**
  - Automatic validation (Pydantic)
  - OpenAPI/Swagger documentation
  - Async support
  - WebSocket support

### Pydantic
- **Use:** Data validation, settings management
- **Why:** Type-safe data models, automatic validation

## Monitoring & Observability

### Prometheus
- **Use:** Metrics collection
- **Why:** Time-series database, flexible querying

### Grafana
- **Use:** Dashboards and visualization
- **Why:** Rich visualization, alerting, plugin ecosystem

### OpenTelemetry
- **Use:** Distributed tracing
- **Why:** Vendor-neutral, rich instrumentation

## CI/CD

### GitHub Actions
- **Use:** Continuous integration and deployment
- **Why:** Native GitHub integration, free for public repos
- **Workflows:**
  - On PR: Lint, test, type-check
  - On push to main: Build, deploy
  - Nightly: Security scans, performance tests

### bun test
- **Use:** Unit tests (frontend)
- **Why:** Fast, integrated with bun

### pytest
- **Use:** Unit tests (backend)
- **Why:** Python standard, rich ecosystem

## Security

### Cloudflare
- **Use:** DDoS protection, WAF, SSL/TLS
- **Why:** Enterprise-grade security, free tier

### UFW Firewall
- **Use:** Server-level firewall
- **Why:** Simple, effective network protection

### GitHub Secret Scanning
- **Use:** Detect leaked credentials
- **Why:** Automated security, protects secrets

## Development Workflow

```bash
# Install dependencies
bun install

# Run development server
bun run dev

# Lint code
bun run lint  # Uses biome

# Format code
bun run format  # Uses biome

# Run tests
bun run test  # Uses bun test

# Build for production
bun run build
```

## Deployment Pipeline

1. **Code Push** → GitHub
2. **CI/CD** → GitHub Actions (lint, test, build)
3. **Deploy Frontend** → Cloudflare Workers (static site)
4. **Deploy Backend** → Kubernetes (FastAPI)
5. **Deploy Database** → Kubernetes (ClickHouse, PostgreSQL)
6. **Monitor** → Prometheus + Grafana

## Performance Targets

- **Frontend Build:** < 30 seconds (bun)
- **API Response:** < 200ms (95th percentile)
- **Query Time:** < 1 second (95th percentile, ClickHouse)
- **Cold Start:** < 100ms (Workers AI)
- **Uptime:** 99.9%+ (3 nines)

## Cost Optimization

- **bun:** Faster builds = lower CI/CD costs
- **biome:** Faster linting = lower compute costs
- **Workers AI:** Pay-as-you-go, no idle costs
- **ClickHouse:** Better compression = lower storage costs
- **Kubernetes:** Efficient resource utilization

## Future Considerations

### Potential Additions
- **Rust WebAssembly (Wasm):** For browser-based data processing
- **Edge Functions:** For personalized content delivery
- **Graph Database (Neo4j):** For complex relationship queries
- **Vector Database (Qdrant):** For semantic search and RAG

### Technology Evaluation Criteria
- Performance benchmarks
- Developer experience
- Community support
- Long-term viability
- Total cost of ownership

---

**Last Updated:** February 16, 2026
**Maintained By:** duyetbot
**Organization:** duet-company
