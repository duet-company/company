# GitHub Operations Skill

GitHub repository management and operations for Duet Company organization.

## 🎯 Purpose

Manages all GitHub operations for duet-company organization including repository creation, access management, issue tracking, CI/CD setup, and release processes.

## 🚀 Usage

```bash
# Via OpenClaw
@duyetbot Create a new repo for the billing service

# Direct invocation
github-skill "List all open PRs across duet-company"

# Repository operations
github-skill "Create feature branch from main"
github-skill "Merge PR #123"
```

## 📚 Dependencies

- GitHub CLI (gh)
- GitHub API
- Organization access
- SSH keys for git operations

## 🔧 Configuration

### Environment Variables

```bash
# GitHub
GH_ORG=duet-company
GH_DEFAULT_BRANCH=main

# Access
GH_TOKEN=***
GH_USER=duyetbot

# Repository Settings
DEFAULT_VISIBILITY=public
DEFAULT_LICENSE=MIT
DEFAULT_BRANCH_PROTECTION=true
```

### Skill Configuration

```yaml
github:
  organization:
    name: ${GH_ORG}
    default_branch: ${GH_DEFAULT_BRANCH}
    default_visibility: ${DEFAULT_VISIBILITY}
    default_license: ${DEFAULT_LICENSE}
    branch_protection: ${DEFAULT_BRANCH_PROTECTION}
  
  access:
    token: ${GH_TOKEN}
    user: ${GH_USER}
  
  repositories:
    naming_convention: kebab-case
    topics: ai-data-labs, duet-company
    template: MIT-licensed, CI-CD-configured
```

## 📖 Examples

### Create New Repository

```markdown
User Request:
"Create a repository for our billing service"

Response:

**Repository Created:**

**Name:** duet-company/billing
**URL:** https://github.com/duet-company/billing
**Description:** Billing and subscription management for AI Data Labs
**Visibility:** Public
**License:** MIT
**Default Branch:** main
**Branch Protection:** Enabled

**Initial Setup:**
- [x] README.md created
- [x] License file added
- [x] .gitignore configured
- [x] Topics added: ai-data-labs, duet-company, billing
- [x] Branch protection on main (PRs required)
- [x] CI/CD workflow template added

**Next Steps:**
1. Add billing service code
2. Set up GitHub Actions for testing
3. Configure deployment pipeline
4. Add documentation link to main repo
5. Update kanboard with initial tasks

**Repository Links:**
- Clone: `git clone git@github.com:duet-company/billing.git`
- Issues: https://github.com/duet-company/billing/issues
- Pull Requests: https://github.com/duet-company/billing/pulls
- Actions: https://github.com/duet-company/billing/actions
```

### List Organization Repositories

```markdown
User Request:
"List all repositories in duet-company organization"

Response:

**duet-company Organization Repositories (16 total):**

**Core Platform (4):**
- platform - Main AI Data Labs platform
- backend - FastAPI backend service
- frontend - React + TypeScript frontend
- infrastructure-config - K8s and Terraform configs

**AI Agents (3):**
- agent-query - Query Agent (NL to SQL)
- agent-design - Platform Designer Agent
- agent-support - Support Agent (24/7 assistance)

**Task Management (2):**
- kanban - Project management and sprint boards
- kanboard - Task board and issue tracking

**Documentation & Strategy (4):**
- vision - Company vision, roadmap, OKRs
- docs - Platform documentation
- playbook - SOPs and onboarding guides
- blog - Company blog

**Infrastructure (2):**
- infrastructure - IaC framework
- scripts - Build and automation scripts

**Skills & Knowledge (1):**
- skills - AI agent skills and documentation

**Organization URL:** https://github.com/duet-company

**Statistics:**
- Total Repositories: 16
- Public: 16 (100%)
- Last Updated: February 16, 2026
```

### Create Pull Request

```markdown
User Request:
"Create a PR for the new query optimization feature"

Response:

**Pull Request Created:**

**Title:** feat: Add query optimization with caching layer

**Branch:** feature/query-optimization → main
**Base:** main
**Head:** feature/query-optimization

**Changes:**
- Add Redis caching layer to query agent
- Implement cache invalidation strategy
- Add cache hit/miss metrics
- Update documentation
- Add unit tests for caching logic

**Files Changed:**
- agents/query/cache.py (new)
- agents/query/__init__.py (modified)
- tests/test_cache.py (new)
- README.md (updated)
- docs/query-optimization.md (new)

**Reviewers:** @duyet
**Labels:** feature, performance, query-agent
**Draft:** No

**PR Link:** https://github.com/duet-company/platform/pull/1

**Next Steps:**
1. CI/CD will run tests automatically
2. Request review from team
3. Address any review comments
4. Merge when approved

**CI/CD Status:** 
- Tests running...
- Lint checks pending...
- Build will start after tests pass...
```

### Review and Merge PR

```markdown
User Request:
"Review and merge PR #123 if it passes all checks"

Response:

**Pull Request #123: feat: Add query optimization with caching layer**

**Status Checks:**
- [✅] Unit tests passed (47/47)
- [✅] Integration tests passed (8/8)
- [✅] Code linting passed
- [✅] Security scan passed (0 vulnerabilities)
- [⏳] Build in progress

**Code Review Summary:**
- Implementation looks good
- Caching strategy is sound
- Tests have good coverage
- Documentation is clear
- Minor: Consider adding cache warming

**Action:** Merge

**Merge Details:**
- Branch: feature/query-optimization → main
- Merge commit: a1b2c3d
- Merge message: Merge pull request #123
- Deletion: feature/query-optimization branch deleted

**Result:** ✅ Merged successfully

**After Merge:**
1. PR #123 closed automatically
2. Issue #456 (feature request) closed with reference to PR
3. Deploy to staging triggered
4. Documentation site updated
5. Release notes added to CHANGELOG.md

**Links:**
- PR: https://github.com/duet-company/platform/pull/123
- Commit: https://github.com/duet-company/platform/commit/a1b2c3d
- Issue: https://github.com/duet-company/kanboard/issues/456
```

### Repository Health Check

```markdown
User Request:
"Check the health of all our repositories"

Response:

**Repository Health Report for duet-company (February 16, 2026)**

| Repository | Branches | Open PRs | Open Issues | Last Commit | Status |
|-----------|-----------|-----------|-------------|--------------|--------|
| platform | 3 | 2 | 15 | 2 hours ago | 🟢 Healthy |
| backend | 2 | 1 | 8 | 1 day ago | 🟢 Healthy |
| frontend | 2 | 0 | 5 | 3 hours ago | 🟢 Healthy |
| agent-query | 1 | 0 | 2 | 5 hours ago | 🟢 Healthy |
| agent-design | 1 | 0 | 3 | 1 day ago | 🟢 Healthy |
| agent-support | 1 | 0 | 1 | 2 days ago | 🟢 Healthy |
| vision | 1 | 0 | 0 | 5 days ago | 🟢 Healthy |
| docs | 1 | 0 | 0 | 3 days ago | 🟢 Healthy |
| playbook | 1 | 0 | 0 | 5 days ago | 🟢 Healthy |
| blog | 1 | 0 | 0 | 5 days ago | 🟢 Healthy |
| infrastructure | 2 | 0 | 0 | 2 days ago | 🟢 Healthy |
| infrastructure-config | 1 | 0 | 0 | 2 days ago | 🟢 Healthy |
| scripts | 1 | 0 | 0 | 2 days ago | 🟢 Healthy |
| kanban | 1 | 0 | 8 | 1 day ago | 🟢 Healthy |
| kanboard | 1 | 0 | 6 | 5 hours ago | 🟢 Healthy |

**Overall Organization Health:**

✅ **All repositories active**
✅ **Default branch is main everywhere**
✅ **No stale issues older than 30 days**
✅ **No security vulnerabilities**
⚠️ **Some open issues need attention**

**Recommendations:**
1. Close kanban issues (8 open)
2. Review and merge open PRs (3 total)
3. Consider reducing branch count in platform and infrastructure

**Total Issues:** 48 open
**Total PRs:** 3 open
**Last Activity:** 2 hours ago (platform)
```

## 🐛 Troubleshooting

### Issue: Cannot create repository

**Possible causes:**
- GitHub token expired
- Organization access revoked
- Repository name conflict
- Rate limit exceeded

**Solutions:**
1. Check auth: `gh auth status`
2. Verify org access: `gh org list`
3. Check existing repos: `gh repo list duet-company`
4. Check rate limit: `gh api rate_limit`
5. Refresh token if needed

### Issue: Branch protection not working

**Possible causes:**
- Insufficient permissions
- Main branch doesn't exist
- Invalid protection rules
- Repository is private

**Solutions:**
1. Check permissions: `gh auth status`
2. Verify main branch: `gh repo view duet-company/platform --json`
3. View protection: `gh api repos/duet-company/platform/branches/main/protection`
4. Update rules: `gh api repos/duet-company/repos --jq .name,.default_branch,.permissions` | gh api put`

### Issue: CI/CD workflow failing

**Possible causes:**
- Workflow syntax error
- Missing secrets
- Runner not available
- Repository not accessible
- Timeout in workflow

**Solutions:**
1. Check workflow syntax: `gh workflow list`
2. View workflow run: `gh run list --repo duet-company/platform`
3. View logs: `gh run view <run-id>`
4. Check secrets: `gh secret list --repo duet-company/platform`
5. Re-run workflow: `gh workflow run <workflow-name> --repo duet-company/platform`

## 📊 GitHub Operations Metrics

### Metrics We Track

| Metric | Target | Current | Status |
|---------|--------|--------|--------|
| Repository Count | 20 | 16 | 🟡 Below target |
| Open Issues | < 50 | 48 | 🟡 Above target |
| Open PRs | < 10 | 3 | 🟢 On target |
| Avg PR Merge Time | < 24 hours | TBD | — |
| Code Coverage | > 80% | TBD | — |
| CI/CD Success Rate | > 95% | TBD | — |

### Repository Standards

All duet-company repos follow these standards:

1. **Branching:** Main + feature branches
2. **PR Title:** `type(scope): description`
3. **Commits:** Conventional commits
4. **License:** MIT for all public repos
5. **Topics:** Standardized tags
6. **Readme:** Comprehensive documentation
7. **.gitignore:** Proper exclusions
8. **CI/CD:** GitHub Actions
9. **Issues:** Templates and labels

## 🔗 Related Skills

- [Company Operations](./company-skill.md) - Overall company management
- [Project Management](./project-skill.md) - Detailed task tracking
- [Query Skill](./query-skill.md) - Query agent GitHub operations
- [Design Skill](./design-skill.md) - Design agent GitHub operations

## 📖 References

- [GitHub Documentation](https://docs.github.com/)
- [GitHub CLI Guide](https://cli.github.com/manual/)
- [GitHub API Docs](https://docs.github.com/en/rest)
- [Duet Company Org](https://github.com/duet-company)

---

**Skill Version:** 1.0.0
**Last Updated:** 2026-02-16
**Maintainer:** Duet Company Operations
