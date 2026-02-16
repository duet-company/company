# Support Skill

24/7 AI-powered customer support agent skill.

## 🎯 Purpose

Provides intelligent, context-aware customer support including answering questions, troubleshooting issues, guiding users through features, and escalating complex problems to human support.

## 🚀 Usage

```bash
# Via OpenClaw
@duyetbot How do I connect my database to the platform?

# Direct invocation
support-skill "My query is running slowly"
```

## 📚 Dependencies

- Knowledge base access (docs/, playbook/)
- Platform backend API
- Issue tracking system
- LLM provider (Claude, GPT-4, or GLM-5)
- Customer data access (with permissions)

## 🔧 Configuration

### Environment Variables

```bash
# Knowledge Base
KNOWLEDGE_BASE=/app/docs
PLAYBOOK_PATH=/app/playbook
FAQ_PATH=/app/docs/support/faq.md

# Platform API
API_BASE_URL=https://api.aidatalabs.ai
API_KEY=***

# Issue Tracking
ISSUE_TRACKER_URL=https://github.com/duet-company/kanboard/issues
ISSUE_TRACKER_TOKEN=***

# LLM
LLM_PROVIDER=claude|openai|zai
LLM_MODEL=claude-3-opus
LLM_API_KEY=***

# Support Settings
MAX_CONTEXT_LENGTH=10000
CONFIDENCE_THRESHOLD=0.8
ESCALATION_THRESHOLD=0.6
AUTO_ESCALATE_HOURS=24
```

### Skill Configuration

```yaml
support:
  knowledge:
    base: ${KNOWLEDGE_BASE}
    playbook: ${PLAYBOOK_PATH}
    faq: ${FAQ_PATH}
  
  api:
    base_url: ${API_BASE_URL}
    key: ${API_KEY}
    timeout: 30
  
  issues:
    tracker: ${ISSUE_TRACKER_URL}
    token: ${ISSUE_TRACKER_TOKEN}
    auto_create: true
  
  llm:
    provider: ${LLM_PROVIDER}
    model: ${LLM_MODEL}
    api_key: ${LLM_API_KEY}
  
  automation:
    max_context: ${MAX_CONTEXT_LENGTH}
    confidence_threshold: ${CONFIDENCE_THRESHOLD}
    escalation_threshold: ${ESCALATION_THRESHOLD}
    auto_escalate_hours: ${AUTO_ESCALATE_HOURS}
```

## 📖 Examples

### Database Connection Issue

```markdown
Customer Question:
"How do I connect my PostgreSQL database to the platform?"

Support Response:

To connect your PostgreSQL database:

1. Go to Settings > Data Sources
2. Click "Add New Source"
3. Select "PostgreSQL"
4. Fill in:
   - Host: your-db-host.com
   - Port: 5432
   - Database: your_database_name
   - Username: your_username
   - Password: ********

5. Click "Test Connection"
6. Once verified, click "Save"

Documentation: /docs/users/database-connection.md
Troubleshooting: /playbook/operations/troubleshooting.md#database-connection
```

### Query Performance Issue

```markdown
Customer Question:
"My query is running slowly, how can I optimize it?"

Support Response:

For slow queries, try these optimizations:

1. **Check Query Plan**
   ```sql
   EXPLAIN <your-query>
   ```
   Look for full table scans or missing indexes.

2. **Add Indexes**
   - Create indexes on WHERE clause columns
   - Create indexes on JOIN columns
   - Consider composite indexes for multi-column filters

3. **Limit Results**
   - Add LIMIT clause when possible
   - Use pagination for large datasets
   - Filter by date range for time-series data

4. **Use Materialized Views**
   - Pre-aggregate common queries
   - Refresh schedule based on data freshness
   - Reduce computation at query time

Tools available:
- Query Optimizer: /tools/optimize-query
- Schema Explorer: /tools/explore-schema

Documentation: /docs/guides/query-optimization.md
```

### Feature Request

```markdown
Customer Request:
"I'd like to see a cohort retention chart"

Support Response:

Great suggestion! Cohort retention analysis is valuable.

Current status:
- ✅ Feature documented in our roadmap
- 🚧 In development (target: Week 6)
- 📋 Planned for Sprint 3

What it will include:
- Cohort assignment based on first action
- Retention curves over time
- Drill-down into specific cohorts
- Export to CSV/PDF

Would you like to:
1. Be notified when it's released?
2. Participate in beta testing?
3. Provide feedback on design?

I can create a feature request and link it to our roadmap.

Documentation: /docs/features/cohort-retention.md
```

## 🐛 Troubleshooting

### Issue: Low confidence in response

**Possible causes:**
- Question not in knowledge base
- Ambiguous requirements
- Missing context
- Feature not yet released

**Solutions:**
1. Ask clarifying questions
2. Check related documentation
3. Suggest manual workaround
4. Escalate to human support

### Issue: Cannot find relevant docs

**Possible causes:**
- Outdated knowledge base
- New feature not documented
- Documentation in wrong location
- Search index issues

**Solutions:**
1. Refresh knowledge base: `support-skill --refresh-kb`
2. Search by keywords: `support-skill --search "topic"`
3. Check playbook: `support-skill --check-playbook`
4. Create documentation gap issue

### Issue: Escalation criteria met

**Possible causes:**
- Complex technical issue
- Security concern
- Feature request
- Service outage

**Solutions:**
1. Check severity level
2. Verify SLA requirements
3. Assign to appropriate team
4. Set priority and timeline
5. Notify customer of escalation

## 📊 Metrics

### Support KPIs

| Metric | Target | Current |
|--------|--------|---------|
| First Response Time | < 5 min | TBD |
| Resolution Time | < 4 hours | TBD |
| First Contact Resolution | > 80% | TBD |
| Customer Satisfaction | > 4.5/5 | TBD |
| Escalation Rate | < 10% | TBD |

### Quality Assurance

1. **Response Validation**
   - Check factual accuracy
   - Verify doc links work
   - Ensure steps are reproducible

2. **Customer Feedback**
   - Rate helpfulness of responses
   - Collect improvement suggestions
   - Track recurring issues

3. **Knowledge Base Updates**
   - Add solutions for new issues
   - Improve existing documentation
   - Remove outdated information

## 🔗 Related Skills

- [Query Skill](./query-skill.md) - Query assistance
- [Design Skill](./design-skill.md) - Platform configuration
- [Ops Skill](./ops-skill.md) - System status

## 📖 References

- [Customer Support Playbook](/playbook/agents/support-agent.md)
- [Troubleshooting Guide](/playbook/operations/troubleshooting.md)
- [FAQ](/docs/support/faq.md)
- [Issue Tracking](https://github.com/duet-company/kanboard)

---

**Skill Version:** 1.0.0
**Last Updated:** 2026-02-16
**Maintainer:** Duet Company AI Team
