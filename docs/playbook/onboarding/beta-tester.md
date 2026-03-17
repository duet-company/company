# Beta Testing Onboarding Guide

**Phase:** Beta Testing (Weeks 9-12)
**Last Updated:** 2026-03-17

---

## Overview

This guide is for beta testers and design partners joining the AI Data Labs platform. It covers everything needed to get started, use the platform effectively, and provide valuable feedback.

---

## Getting Started

### 1. Account Setup

Once your account is created, you'll receive:

- **Email:** `hello@aidatalabs.ai` with login credentials
- **Login URL:** `https://app.aidatalabs.ai` (after domain setup)
- **Initial Access:** Read-write permissions on your workspace

### 2. First Login

1. Visit the login URL
2. Enter your email and temporary password
3. Change your password on first login
4. Complete your profile (name, timezone, notification preferences)

### 3. Dashboard Overview

The dashboard provides:
- **Platform Status:** System health and uptime
- **Quick Actions:** Create query, design platform, chat with agents
- **Recent Activity:** Last 10 queries and tasks
- **Resource Usage:** Storage, query count, agent calls

---

## Core Features

### Natural Language Query (Query Agent)

**What it does:** Convert natural language questions into SQL queries and get instant results.

**How to use:**
1. Click "New Query" in the dashboard
2. Type your question in natural language (e.g., "Show me sales by region for last month")
3. The AI generates optimized SQL and displays results
4. Export to CSV, save as dashboard, or refine the query

**Example queries:**
- "What's our average response time by channel?"
- "Show top 10 products by revenue this quarter"
- "How many users signed up in the last 7 days?"

**Tips for better results:**
- Be specific about time ranges (e.g., "last month" vs "2025-02")
- Mention aggregation if needed (e.g., "sum," "average," "count")
- Specify filters (e.g., "where status = active")

---

### Platform Designer Agent

**What it does:** Design and deploy data platforms from natural language descriptions.

**How to use:**
1. Click "Design Platform" in the dashboard
2. Describe your data platform needs in natural language
3. The AI generates:
   - Database schema
   - Infrastructure configuration
   - Kubernetes manifests
   - API endpoints
   - Dashboard templates

**Example prompts:**
- "Create an e-commerce analytics platform with sales, customers, and inventory tables"
- "Design a real-time IoT sensor data pipeline with ClickHouse"
- "Build a customer support ticket tracking system with analytics"

**What happens after design:**
1. Review the generated schema and configuration
2. Approve or request changes
3. The platform provisions infrastructure automatically
4. Database and APIs are deployed
5. Dashboard templates are available

---

### Multi-Agent Chat

**What it does:** Chat with AI agents to get help with queries, designs, and platform operations.

**Available agents:**
- **Query Agent:** Help with SQL and data questions
- **Platform Designer Agent:** Help with platform design
- **Support Agent:** Help with troubleshooting and platform issues

**How to use:**
1. Click "Chat" in the dashboard
2. Select the agent you want to work with
3. Ask your question or describe your problem
4. The agent responds with actionable solutions

**Example interactions:**
- "Query Agent: How do I calculate moving average in ClickHouse?"
- "Platform Designer Agent: Can you help me add a new table to my schema?"
- "Support Agent: My query is running slow, can you help optimize it?"

---

### Monitoring & Observability

**What it does:** Real-time monitoring of platform health, query performance, and resource usage.

**Key metrics:**
- **Platform Uptime:** Current availability (target: 99.9%)
- **Query Latency:** Average query response time
- **Active Users:** Number of concurrent users
- **Storage Usage:** Data storage by workspace
- **Agent Calls:** Number of AI agent requests

**Grafana Dashboards:**
- **Platform Health:** Overall system status
- **Query Performance:** Response times and error rates
- **Resource Utilization:** CPU, memory, storage, network
- **Agent Metrics:** Agent performance and usage

---

## Beta Testing Guidelines

### What We're Testing

1. **Core Functionality**
   - Query accuracy and relevance
   - Platform designer schema generation
   - Agent response quality
   - Dashboard usability

2. **Performance**
   - Query response times (target: <1s for 95% of queries)
   - Platform stability and uptime
   - Resource efficiency

3. **User Experience**
   - Ease of navigation
   - Intuitiveness of features
   - Quality of documentation
   - Onboarding experience

4. **Edge Cases**
   - Complex queries
   - Large datasets
   - Multiple concurrent users
   - Unusual data schemas

### How to Report Issues

**For bugs:**
1. Use the "Report Issue" button in the dashboard
2. Include:
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots (if applicable)
   - Browser/console errors (if any)

**For feature requests:**
1. Use "Feature Request" in the help menu
2. Describe the feature and use case
3. Explain how it would help your workflow

**For general feedback:**
1. Use the "Send Feedback" option
2. Rate features (1-5 stars)
3. Add comments about your experience

### Feedback Priority

We're prioritizing feedback on:
1. **Query accuracy:** Are results correct and relevant?
2. **Response time:** Are queries fast enough?
3. **Platform designer:** Does it generate usable schemas?
4. **Usability:** Is the interface intuitive?

---

## Best Practices

### For Natural Language Queries

✅ **Good:**
- "Show me total revenue by month for 2025"
- "What's the average order value by customer segment?"
- "Find users who signed up but haven't made a purchase"

❌ **Avoid:**
- "Show data" (too vague)
- "Give me everything" (not specific enough)
- "Something about sales" (unclear objective)

### For Platform Designer

✅ **Good:**
- "Create an analytics platform for an e-commerce store with products, orders, and customers tables. Track sales metrics and customer lifetime value."
- "Design a sensor data pipeline for IoT devices with time-series data and alerts for anomalies."

❌ **Avoid:**
- "Make a database" (not specific)
- "Do analytics" (missing context)
- "I need data" (unclear requirements)

### For Effective Beta Testing

1. **Test real use cases:** Try queries that mirror your actual work
2. **Iterate:** Refine queries and see how the AI learns
3. **Push boundaries:** Try complex, unusual queries
4. **Document:** Keep notes on what works well and what doesn't
5. **Communicate:** Share feedback regularly, not just at the end

---

## Known Limitations

### Query Agent
- Maximum query complexity: Limited to single-table joins for beta
- Result set size: Limited to 10,000 rows per query
- Supported databases: ClickHouse, PostgreSQL (beta)

### Platform Designer
- Maximum tables per schema: 10 for beta
- Supported deployment: Kubernetes only (beta)
- Custom integrations: Limited during beta

### Platform
- Maximum concurrent users: 5 per workspace (beta limit)
- Storage quota: 100GB per workspace (beta limit)
- Query quota: 1,000 queries per day (beta limit)

---

## Support & Communication

### Getting Help

1. **In-app chat:** Use the "Ask Support" option
2. **Email:** support@aidatalabs.ai
3. **Documentation:** https://docs.aidatalabs.ai (coming soon)
4. **Community:** Join our Discord (invite link coming soon)

### Office Hours

We'll hold weekly office hours for beta testers:
- **Time:** Thursdays, 2:00 PM - 3:00 PM CET
- **Format:** Zoom call
- **Purpose:** Live Q&A, feature walkthroughs, feedback discussion

### Updates

We'll share weekly updates via:
- Email newsletter
- In-app notifications
- Discord announcements

---

## Beta Testing Timeline

**Week 1: Onboarding & Basics**
- Account setup and dashboard tour
- Try basic queries
- Test platform designer with simple schemas

**Week 2: Deep Dive**
- Test complex queries
- Try multi-table schemas
- Test multi-agent chat

**Week 3: Stress Testing**
- Push query complexity limits
- Test with larger datasets
- Test concurrent user scenarios

**Week 4: Feedback & Iteration**
- Comprehensive feedback submission
- Feature requests
- Review of beta learnings

---

## Success Metrics

We're tracking these metrics during beta:

| Metric | Target |
|--------|--------|
| Query accuracy | >90% |
| Query response time (p95) | <1s |
| Platform uptime | >99.9% |
| User satisfaction (NPS) | >50 |
| Bugs fixed per week | 10+ |
| Feature requests captured | 20+ |

---

## Frequently Asked Questions

**Q: Is my data secure during beta?**
A: Yes. All data is encrypted at rest and in transit. We follow industry best practices for security.

**Q: Will my data be deleted after beta?**
A: No. Your data will be migrated to production when we launch, or you can export it at any time.

**Q: Can I invite team members?**
A: Yes, you can invite up to 5 team members per workspace during beta.

**Q: What happens if I find a bug?**
A: Report it using the in-app feedback form. We'll investigate and prioritize fixes.

**Q: Can I suggest new features?**
A: Absolutely! Feature requests are highly valued. Use the feedback form to submit ideas.

**Q: How long does beta last?**
A: The beta period is 4 weeks, with potential extensions based on feedback.

---

## Next Steps

1. **Complete setup:** Log in and explore the dashboard
2. **Try basic queries:** Start with simple questions
3. **Test platform designer:** Design a small schema
4. **Join Discord:** Connect with other beta testers
5. **Attend office hours:** Ask questions live
6. **Provide feedback:** Help us improve

---

**Need help?** Email support@aidatalabs.ai or use the in-app chat.

**Thank you for being a beta tester!** Your feedback is invaluable in shaping AI Data Labs.

---

*This guide is a living document and will be updated throughout the beta period.*
