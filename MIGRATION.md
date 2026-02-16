# Monorepo Migration Plan

This document outlines the migration from individual repositories to the new `duet-company/company` monorepo.

## ✅ New Monorepo

**Repository:** https://github.com/duet-company/company

**Status:** ✅ Created and initialized

**Structure:**
```
company/
├── apps/
│   ├── frontend/     # React + TypeScript dashboard
│   ├── backend/      # FastAPI backend service
│   └── api/         # API gateway (to be added)
├── packages/
│   ├── shared/      # Shared utilities
│   ├── types/       # TypeScript types
│   └── config/      # Shared configuration
├── agents/
│   ├── query/       # Query Agent (NL to SQL)
│   ├── design/      # Design Agent (infrastructure)
│   └── support/     # Support Agent (24/7)
├── docs/           # Technical documentation
├── infrastructure/ # IaC (Terraform, K8s)
└── scripts/        # Build and automation
```

## 📦 Repositories Status

### ✅ Keep (Independent)

These repositories serve specific purposes and should remain separate:

1. **company** - NEW monorepo containing all company code
2. **vision** - Company vision, OKRs, roadmap (strategic documentation)
3. **skills** - OpenClaw-compatible AI agent skills (external tools)
4. **docs** - Platform documentation and user guides (or move to monorepo docs/)

### 🗄️ Archive (Consolidated into Monorepo)

These repositories are now redundant and should be archived:

| Repository | New Location | Action |
|------------|--------------|--------|
| backend | company/apps/backend | Archive |
| frontend | company/apps/frontend | Archive |
| infrastructure-config | company/infrastructure | Archive |
| scripts | company/scripts | Archive |
| agent-query | company/agents/query | Archive |
| agent-design | company/agents/design | Archive |
| agent-support | company/agents/support | Archive |
| kanban | company/docs (optional) | Archive |
| kanboard | company/docs (optional) | Archive |
| blog | company/docs (optional) | Archive |
| playbook | company/docs (optional) | Archive |
| infrastructure | company/infrastructure | Archive |
| platform | company (replaced) | Archive |
| test-repo | - | Delete |
| ai-data-labs | - | Delete |

## 🔧 Manual Actions Required

### Step 1: Archive Redundant Repositories

For each repository in the "Archive" table:

1. Go to repository settings
2. Scroll to "Danger Zone"
3. Click "Archive this repository"

**GitHub Archive Links:**
- https://github.com/duet-company/backend/settings
- https://github.com/duet-company/frontend/settings
- https://github.com/duet-company/infrastructure-config/settings
- https://github.com/duet-company/scripts/settings
- https://github.com/duet-company/agent-query/settings
- https://github.com/duet-company/agent-design/settings
- https://github.com/duet-company/agent-support/settings
- https://github.com/duet-company/kanban/settings
- https://github.com/duet-company/kanboard/settings
- https://github.com/duet-company/blog/settings
- https://github.com/duet-company/playbook/settings
- https://github.com/duet-company/infrastructure/settings
- https://github.com/duet-company/platform/settings

### Step 2: Delete Empty/Unused Repositories

Delete these repositories completely:

1. https://github.com/duet-company/test-repo
2. https://github.com/duet-company/ai-data-labs

### Step 3: Update GitHub Description (Optional)

Update the organization description to reflect the monorepo structure:

> "Duet Company - AI Data Labs. Monorepo-based development with bun, biome, TypeScript, and FastAPI."

## 📊 Final Repository Structure

After migration, the organization will have:

**Active Repositories (4):**
1. **company** - Main monorepo (all code)
2. **vision** - Strategic documents
3. **skills** - OpenClaw skills
4. **docs** - Documentation (optional - could be in monorepo)

**Archived Repositories (13):**
- All redundant repositories archived

**Deleted Repositories (2):**
- test-repo, ai-data-labs

## 🔄 Migration Benefits

**Simplified Structure:**
- Single source of truth for all code
- Easier cross-package development
- Shared dependencies and tooling

**Better Developer Experience:**
- One clone command
- Unified CI/CD pipeline
- Consistent tooling (bun, biome)

**Reduced Maintenance:**
- Fewer repositories to manage
- Consistent configuration
- Simplified documentation

## 📝 Notes

- **Backwards Compatibility:** Old repositories will remain accessible via their archived URLs
- **Redirects:** GitHub automatically handles redirects from archived repos
- **History:** All commit history is preserved in archived repositories
- **Monorepo Growth:** The monorepo can grow to include more apps/packages as needed

---

**Migration Date:** February 16, 2026
**Status:** Monorepo created, awaiting manual archival of old repos
**Maintained By:** duyetbot
