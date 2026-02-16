# Project Management Skill

Detailed project tracking, sprint management, and task coordination for Duet Company.

## 🎯 Purpose

Provides comprehensive project management including sprint planning, task breakdown, time tracking, dependency management, and milestone coordination for AI Data Labs development.

## 🚀 Usage

```bash
# Via OpenClaw
@duyetbot Break down the authentication system feature into tasks

# Direct invocation
project-skill "Create sprint plan for Week 3"

# Task tracking
project-skill "Update task #45 status to in-progress"
```

## 📚 Dependencies

- Kanboard (task board)
- Vision (OKRs and roadmap)
- Docs (feature specifications)
- GitHub issues and PRs
- Team availability

## 🔧 Configuration

### Environment Variables

```bash
# Project Management
KANBOARD=https://github.com/duet-company/kanboard
KANBOARD_REPO=duet-company/kanboard

# Sprint Settings
SPRINT_DURATION_WEEKS=2
SPRINT_START_DAY=Monday
SPRINT_VELOCITY_TARGET=20

# Task Estimation
STORY_POINT_DAY=8
TASK_MIN_DAYS=0.5
TASK_MAX_DAYS=5

# Labels
PRIORITY_LABELS=critical,high,medium,low
TYPE_LABELS=feature,bug,refactor,docs,design,test
STATUS_LABELS=ready,in-progress,in-review,done,blocked
```

### Skill Configuration

```yaml
project:
  kanboard:
    url: ${KANBOARD}
    repo: ${KANBOARD_REPO}
  
  sprint:
    duration_weeks: ${SPRINT_DURATION_WEEKS}
    start_day: ${SPRINT_START_DAY}
    velocity_target: ${SPRINT_VELOCITY_TARGET}
  
  estimation:
    story_point_day: ${STORY_POINT_DAY}
    task_min_days: ${TASK_MIN_DAYS}
    task_max_days: ${TASK_MAX_DAYS}
  
  labels:
    priority: ${PRIORITY_LABELS}
    type: ${TYPE_LABELS}
    status: ${STATUS_LABELS}
```

## 📖 Examples

### Feature Breakdown

```markdown
User Request:
"Break down the authentication system feature into tasks"

Response:

**Feature:** Authentication System for AI Data Labs Platform
**Estimated Story Points:** 21
**Target Sprint:** Sprint 2 (Weeks 3-4)

**Task Breakdown:**

#### 1. User Registration (5 points)
**Description:** Implement user sign-up and login functionality
**Tasks:**
- [ ] Design database schema for users table
- [ ] Implement password hashing (bcrypt)
- [ ] Create user registration API endpoint
- [ ] Create login API endpoint
- [ ] Add email verification
- [ ] Write unit tests
- [ ] Add API documentation
**Estimated Days:** 5
**Dependencies:** None
**Assignee:** @backend-team

#### 2. Session Management (3 points)
**Description:** Handle user sessions and tokens
**Tasks:**
- [ ] Design session storage (Redis)
- [ ] Implement token generation
- [ ] Create session validation middleware
- [ ] Implement token refresh logic
- [ ] Add session expiration
- [ ] Write unit tests
**Estimated Days:** 3
**Dependencies:** User registration complete
**Assignee:** @backend-team

#### 3. OAuth Integration (8 points)
**Description:** Add OAuth2 support for Google and GitHub
**Tasks:**
- [ ] Research OAuth2 flow
- [ ] Configure provider credentials
- [ ] Implement authorization code flow
- [ ] Create OAuth callback endpoint
- [ ] Add token exchange logic
- [ ] User profile synchronization
- [ ] Add revocation endpoint
- [ ] Write integration tests
**Estimated Days:** 8
**Dependencies:** Session management complete
**Assignee:** @backend-team

#### 4. Permission System (5 points)
**Description:** Implement role-based access control
**Tasks:**
- [ ] Define permission schema (admin, user, viewer)
- [ ] Create permissions database table
- [ ] Implement permission checking middleware
- [ ] Add permission assignment API
- [ ] Create permission management UI
- [ ] Write permission tests
- [ ] Document permission system
**Estimated Days:** 5
**Dependencies:** OAuth integration complete
**Assignee:** @backend-team

**Total Story Points:** 21
**Total Estimated Days:** 21 (3.5 weeks)
**Sprint Capacity:** 20 points (2.5 weeks)

**Risk:** Feature may need to be split across 2 sprints

**Next Actions:**
1. Create GitHub issues for each task
2. Add to kanboard Sprint 2
3. Assign to backend team
4. Monitor dependencies and adjust timeline

Documentation:
- Kanboard: https://github.com/duet-company/kanboard
- Feature Spec: https://github.com/duet-company/docs/blob/main/features/authentication.md
```

### Sprint Planning

```markdown
User Request:
"Create sprint plan for Week 3 (MVP Development)"

Response:

**Sprint 2: MVP Development (Weeks 3-4)**
**Sprint Goal:** Complete all core AI agents and basic platform infrastructure
**Sprint Duration:** 2 weeks
**Capacity:** 20 story points
**Start Date:** March 9, 2026 (Monday)
**End Date:** March 23, 2026 (Sunday)

**Backlog Items Selected (20 points):**

#### High Priority (12 points):
1. **Query Agent Implementation** (5 points)
   - NL to SQL translation engine
   - Query optimization and caching
   - Error handling and retry logic
   - Assignee: @ai-team
   - Dependencies: None

2. **Platform Designer Agent** (5 points)
   - Requirement parsing engine
   - Schema design automation
   - Infrastructure provisioning
   - Assignee: @ai-team
   - Dependencies: None

3. **Authentication System** (5 points) - BREAKDOWN
   - User registration and login (2 points)
   - Session management (1 point)
   - Permission system (2 points)
   - Assignee: @backend-team
   - Dependencies: Infrastructure

#### Medium Priority (8 points):
4. **Frontend Skeleton** (4 points)
   - React + TypeScript setup
   - Basic routing and layout
   - API client integration
   - Assignee: @frontend-team
   - Dependencies: None

5. **Monitoring Setup** (4 points)
   - Prometheus + Grafana deployment
   - Alert configuration
   - Dashboard creation
   - Assignee: @ops-team
   - Dependencies: Infrastructure

**Dependencies:**
- Infrastructure must be complete before Authentication, Monitoring
- Backend API needed for Frontend
- All agents must work before end of sprint

**Sprint Risks:**
- High: Infrastructure not ready by Week 3 start
- Medium: Team capacity limited
- Low: Unknown complexity in agent implementations

**Sprint Goals:**
- [ ] Complete Query Agent with caching
- [ ] Complete Platform Designer Agent
- [ ] Ship authentication system
- [ ] Deploy monitoring stack
- [ ] Create frontend skeleton
- [ ] Maintain 0 blocked items
- [ ] Achieve sprint velocity of 20 points

**Review Date:** March 23, 2026
**Retro Date:** March 24, 2026

**Links:**
- Kanboard: https://github.com/duet-company/kanboard/issues
- Roadmap: https://github.com/duet-company/vision/blob/main/ROADMAP.md#phase-2-mvp-development-weeks-5-8
```

### Task Status Update

```markdown
User Request:
"Update task #45 status to in-progress"

Response:

**Task #45 Updated:**

**Title:** Implement user registration API endpoint
**Repository:** duet-company/backend
**Issue:** https://github.com/duet-company/backend/issues/45

**Status Change:** ready → in-progress

**Updated Details:**
- **Status:** 🔄 In Progress
- **Assignee:** @duyet
- **Started:** February 16, 2026, 2:07 PM UTC
- **Labels:** feature, backend, authentication, in-progress
- **Estimated Completion:** February 18, 2026

**Progress Update Added:**
"Started implementing user registration endpoint. Will include email verification and password hashing. ETA: 2 days."

**Next Actions:**
1. Clone backend repository
2. Create feature branch from main
3. Implement user registration endpoint
4. Write unit tests
5. Update task status as work progresses
6. Create PR when complete
7. Link PR to task
8. Update task to review status

**Related Issues:**
- #44 - User login endpoint (blocked by #45)
- #46 - Password hashing library (depends on #45)

**Sprint Impact:**
- Sprint 1: Now 3/8 tasks in progress
- Velocity: 3 story points completed this week
- Remaining capacity: 17 story points
```

### Dependency Management

```markdown
User Request:
"Show me the dependency graph for authentication feature"

Response:

**Authentication Feature Dependency Graph:**

```
┌─────────────────────────────────────────────────────────────┐
│ Authentication Feature (21 story points)          │
│ ┌─────────────┬─────────────┬─────────────┐│
│ │User Reg    │Session Mgmt  │OAuth2       ││
│ │(5 pts)     │(3 pts)     │(8 pts)     ││
│ └─────┬───────┴───────┬───────┘│
│       │               │       │     ││
│ ▼               │       ▼       ▼     ││
│ Perm System │Token Gen │Provider  │   │
│ │(5 pts)    │(1 pt)  │Config  │   │
│ └─────────────┴──────────────┘     │
│                                     │
│                                 ▼
│                            Infrastructure (4 pts)
│
└──────────────────────────────────────────────────────┘

Critical Path: User Reg → Session Mgmt → OAuth2 → Perm System (15 days)
                    │
                    └──→ Auth Complete (20 days)

Parallel Tasks:
- Query Agent (can start now)
- Platform Designer (can start now)
- Frontend Skeleton (can start now)
- Monitoring Setup (wait for infra)

Total Timeline: 20-25 days for authentication complete

Blockers:
- ⚠️ Infrastructure must be ready before Auth can deploy to staging
- ⚠️ OAuth2 credentials must be configured before integration testing

Recommendation:
Prioritize infrastructure setup (4 days) to unblock authentication development
```

## 🐛 Troubleshooting

### Issue: Task stuck in "in-progress" too long

**Possible causes:**
- Task underestimated
- Team member unavailable
- Technical blockage
- Dependencies not met
- Scope creep

**Solutions:**
1. Check task age: `github-skill --stale-tasks`
2. Update estimate: Increase story points or days
3. Break down further: Create sub-tasks
4. Reassign: Move to available team member
5. Document blocker: Update task with specific issue
6. Consider removing from sprint: If truly blocked

### Issue: Sprint velocity too low

**Possible causes:**
- Tasks too large
- Context switching
- Unexpected bugs
- Technical debt
- Poor estimation

**Solutions:**
1. Reduce task size: Break into smaller units
2. Focus time: Eliminate distractions
3. Timebox tasks: Strict time limits
4. Improve estimation: Use historical data
5. Reduce WIP: Limit concurrent tasks to 2-3
6. Technical debt: Allocate time in sprint

### Issue: Too many blocked tasks

**Possible causes:**
- Dependencies not clear
- External blockers
- Missing resources
- Poor planning

**Solutions:**
1. Identify root causes: Analyze blocker patterns
2. Unblock dependencies: Prioritize dependency tasks
3. Alternative solutions: Work around blockers
4. Resource allocation: Add team members
5. Adjust timeline: Update sprint plan
6. Communicate blockers: Update stakeholders

## 📊 Project Metrics

### Sprint Metrics

| Metric | Target | Current | Status |
|---------|--------|--------|--------|
| Story Points Completed | 20 | TBD | — |
| Tasks Completed | 8-10 | TBD | — |
| On-Time Delivery | 90% | TBD | — |
| Blockers | < 2 | TBD | — |
| Cycle Time | < 5 days | TBD | — |
| Reopened Rate | < 10% | TBD | — |

### Quality Metrics

| Metric | Target | Current | Status |
|---------|--------|--------|--------|
| Code Coverage | > 80% | TBD | — |
| Test Pass Rate | > 95% | TBD | — |
| Bug Escape Rate | < 5% | TBD | — |
| Review Time | < 48 hours | TBD | — |

## 🔗 Related Skills

- [Company Operations](./company-skill.md) - Overall company management
- [GitHub Operations](./github-skill.md) - Repository management
- [Kanban](../kanboard/README.md) - Task board setup
- [Vision](https://github.com/duet-company/vision) - OKRs and roadmap

## 📖 References

- [Kanboard](https://github.com/duet-company/kanboard)
- [Roadmap](https://github.com/duet-company/vision/blob/main/ROADMAP.md)
- [OKRs](https://github.com/duet-company/vision/blob/main/OKR.md)

---

**Skill Version:** 1.0.0
**Last Updated:** 2026-02-16
**Maintainer:** Duet Company Project Management
