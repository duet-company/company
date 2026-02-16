# Company Operations Skill

Overall company management and operations for Duet Company.

## 🎯 Purpose

Provides high-level company operations including strategy execution, project management, team coordination, business metrics, and organizational processes.

## 🚀 Usage

```bash
# Via OpenClaw
@duyetbot Give me an overview of our current sprint status

# Direct invocation
company-skill "Show Q1 OKR progress"

# Weekly review
company-skill "What are our top priorities this week?"
```

## 📚 Dependencies

- GitHub API (via gh CLI)
- Project tracking system (kanboard)
- OKR system (vision repo)
- Documentation (docs repo)
- Issue tracking (kanban)

## 🔧 Configuration

### Environment Variables

```bash
# GitHub
GH_ORG=duet-company
GH_DEFAULT_BRANCH=main

# Project Management
KANBOARD_URL=https://github.com/duet-company/kanboard

# Documentation
DOCS_URL=https://github.com/duet-company/docs
VISION_URL=https://github.com/duet-company/vision

# Company Settings
COMPANY_NAME=Duet Company
PRODUCT_NAME=AI Data Labs
FOUNDER=duyet
FOUNDED=2025

# LLM
LLM_PROVIDER=claude|openai|zai
LLM_MODEL=claude-3-opus
LLM_API_KEY=***
```

### Skill Configuration

```yaml
company:
  github:
    org: ${GH_ORG}
    default_branch: ${GH_DEFAULT_BRANCH}
  
  projects:
    kanboard: ${KANBOARD_URL}
    docs: ${DOCS_URL}
    vision: ${VISION_URL}
  
  settings:
    name: ${COMPANY_NAME}
    product: ${PRODUCT_NAME}
    founder: ${FOUNDER}
    founded: ${FOUNDED}
  
  llm:
    provider: ${LLM_PROVIDER}
    model: ${LLM_MODEL}
    api_key: ${LLM_API_KEY}
```

## 📖 Examples

### Sprint Status Check

```markdown
User Request:
"Give me an overview of our current sprint status"

Response:

**Current Sprint:** Sprint 1 (Weeks 1-2)
**Goal:** Foundation and Infrastructure Setup

**Task Progress:**
- [✅] Set up company registration
- [✅] Acquire domain aidatalabs.ai
- [🔄] Provision VPS infrastructure
- [ ] Setup Kubernetes cluster
- [ ] Deploy ClickHouse database
- [ ] Setup monitoring stack
- [ ] Create CI/CD pipelines

**Metrics:**
- Tasks completed: 2/8 (25%)
- Blocked: 0
- Velocity: 2 story points/week

**Risks:**
- Infrastructure provisioning taking longer than expected
- Need to select VPS provider

**Next Actions:**
1. Select and provision VPS this week
2. Complete K8s setup by end of Week 2
3. Start ClickHouse deployment

Documentation:
- Kanboard: https://github.com/duet-company/kanboard/issues
- Roadmap: https://github.com/duet-company/vision/blob/main/ROADMAP.md
```

### OKR Progress Check

```markdown
User Request:
"Show Q1 OKR progress"

Response:

**Q1 2025 OKRs (Weeks 1-12)**

### Objective 1: Build Production-Ready MVP
**Progress: 25% (2/8 KRs complete)

✅ KR1.1: Complete core platform with 3 AI agents - IN PROGRESS
❌ KR1.2: Achieve 99% uptime in beta testing phase - NOT STARTED
❌ KR1.3: Average query response time <1 second - NOT STARTED
❌ KR1.4: Pass security audit with no critical findings - NOT STARTED

### Objective 2: Validate Market Fit
**Progress: 0% (0/4 KRs complete)

❌ KR2.1: Acquire 5 beta customers by Week 10 - NOT STARTED
❌ KR2.2: Achieve NPS score >50 from beta users - NOT STARTED
❌ KR2.3: Convert 60% of beta users to paid customers - NOT STARTED
❌ KR2.4: Gather 50+ actionable feature requests - NOT STARTED

### Objective 3: Establish Infrastructure & Operations
**Progress: 0% (0/4 KRs complete)

❌ KR3.1: Deploy production infrastructure on Kubernetes by Week 4 - IN PROGRESS
❌ KR3.2: Implement CI/CD pipeline with <10min deployment time - NOT STARTED
❌ KR3.3: Setup monitoring with alerts for all critical services - NOT STARTED
❌ KR3.4: Achieve cost efficiency <$100/TB/month - NOT STARTED

**Overall Q1 Progress: 8% (2/24 KRs complete)

**Critical Path:**
1. Complete infrastructure provisioning (KR3.1) - BLOCKING other work
2. Finish MVP development (KR1.1) - BLOCKS beta testing

**Recommended Actions:**
1. Prioritize VPS selection and provisioning
2. Start Kubernetes deployment immediately after VPS ready
3. Prepare beta customer outreach materials
4. Schedule security audit

Documentation:
- Full OKRs: https://github.com/duet-company/vision/blob/main/OKR.md
```

### Weekly Priorities Review

```markdown
User Request:
"What are our top priorities this week?"

Response:

**Week of:** February 17-23, 2026

**Top 3 Priorities:**

### Priority 1: Complete Infrastructure Setup
**Why:** Blocks all development work
**Deadline:** End of Week 2 (March 2)
**Tasks:**
- [ ] Select VPS provider (DigitalOcean/Hetzner)
- [ ] Provision VPS with minimum specs
- [ ] Setup Kubernetes cluster (microk8s)
- [ ] Deploy ClickHouse
- [ ] Setup monitoring (Prometheus + Grafana)

**Owner:** Duyet
**Dependencies:** None

---

### Priority 2: Start MVP Development
**Why:** Critical path to launch
**Deadline:** Start Week 3 (March 9)
**Tasks:**
- [ ] Complete Query Agent implementation
- [ ] Complete Platform Designer Agent
- [ ] Build authentication system
- [ ] Create basic UI framework
- [ ] Connect to ClickHouse

**Owner:** Engineering Team
**Dependencies:** Infrastructure setup complete

---

### Priority 3: Company Registration & Brand
**Why:** Legal and branding foundations
**Deadline:** End of Week 2 (March 2)
**Tasks:**
- [ ] Register company (Singapore C-Corp)
- [ ] Acquire domain aidatalabs.ai
- [ ] Design brand identity (logo, colors)
- [ ] Create brand guidelines document

**Owner:** Duyet
**Dependencies:** Budget approval

**Blockers:**
- None currently

**Risk:**
- VPS provisioning delays could push MVP development

Documentation:
- Kanboard: https://github.com/duet-company/kanboard
- Roadmap: https://github.com/duet-company/vision/blob/main/ROADMAP.md
```

### Business Metrics Overview

```markdown
User Request:
"Show our current business metrics"

Response:

**Business Metrics as of:** February 16, 2026

### Product Development
- **Platform Status:** Foundation (Weeks 1-4)
- **MVP Target:** Week 8
- **Launch Target:** Week 16

### Development Metrics
- **Sprint:** Sprint 1 (Weeks 1-2)
- **Tasks Complete:** 2/8 (25%)
- **Blocked:** 0
- **Velocity:** TBD

### Repository Activity
- **Total Repos:** 16
- **Active Development:** platform, backend, frontend, agents
- **Last Update:** February 16, 2026

### OKR Progress
- **Q1 2025:** 8% complete (2/24 KRs)
- **On Track:** ❌ No - infrastructure delay

### Launch Timeline
- **Weeks to Launch:** 16
- **Current Week:** 2
- **Weeks Remaining:** 14

### Risk Summary
- **High Risk:** Infrastructure setup delayed
- **Medium Risk:** VPS provider selection pending
- **Low Risk:** Development resource allocation

**Recommended Focus:**
1. Unblock infrastructure setup immediately
2. Prioritize critical path tasks
3. Prepare contingency plan for delays

Documentation:
- Full OKRs: https://github.com/duet-company/vision/blob/main/OKR.md
- Roadmap: https://github.com/duet-company/vision/blob/main/ROADMAP.md
```

## 🐛 Troubleshooting

### Issue: Cannot find kanboard issues

**Possible causes:**
- GitHub token expired
- Repository not accessible
- Kanboard not configured

**Solutions:**
1. Check GitHub auth: `gh auth status`
2. Verify repository access: `gh repo view duet-company/kanboard`
3. Check network connectivity to GitHub
4. Refresh kanboard data if available

### Issue: OKRs not loading

**Possible causes:**
- Vision repo not accessible
- File format changed
- Parsing error

**Solutions:**
1. Check vision repo: `gh repo view duet-company/vision`
2. Verify OKR.md exists
3. Try direct URL: `https://github.com/duet-company/vision/blob/main/OKR.md`
4. Check file format and encoding

### Issue: Documentation links broken

**Possible causes:**
- Repository renamed
- File moved
- Incorrect path

**Solutions:**
1. Verify docs repo structure: `gh repo view duet-company/docs`
2. Check file exists: `gh api repos/duet-company/contents/docs/README.md`
3. Update broken links
4. Use absolute URLs when needed

## 📊 Company Metrics

### KPIs We Track

| Category | Metric | Target | Current | Status |
|----------|--------|--------|--------|
| Development | Sprint velocity | TBD | TBD | — |
| Development | Task completion rate | 80% | TBD | — |
| Product | Features per sprint | 4-6 | TBD | — |
| Business | OKR completion | 100%/quarter | 8% Q1 | ⚠️ |
| Business | On-time delivery | 90% | TBD | — |
| Infrastructure | Uptime | 99.9% | TBD | — |
| Infrastructure | Cost efficiency | <$100/TB/mo | TBD | — |

### Launch Progress

| Phase | Start | End | Status | Completion |
|-------|-------|-----|--------|------------|
| Phase 1: Foundation | Week 1 | Week 4 | 🔄 In Progress | 25% |
| Phase 2: MVP | Week 5 | Week 8 | ⏳ Not Started | 0% |
| Phase 3: Beta | Week 9 | Week 12 | ⏳ Not Started | 0% |
| Phase 4: Launch | Week 13 | Week 16 | ⏳ Not Started | 0% |

## 🔗 Related Skills

- [Project Management](./project-skill.md) - Detailed project tracking
- [GitHub Operations](./github-skill.md) - Repository management
- [Team Coordination](./team-skill.md) - Team communication
- [Business Development](./business-skill.md) - Sales and marketing

## 📖 References

- [Company Vision](https://github.com/duet-company/vision)
- [Roadmap](https://github.com/duet-company/vision/blob/main/ROADMAP.md)
- [OKRs](https://github.com/duet-company/vision/blob/main/OKR.md)
- [Documentation](https://github.com/duet-company/docs)
- [Project Board](https://github.com/duet-company/kanboard)

---

**Skill Version:** 1.0.0
**Last Updated:** 2026-02-16
**Maintainer:** Duet Company Operations
