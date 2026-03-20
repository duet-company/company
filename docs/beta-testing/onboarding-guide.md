# Beta Testing Onboarding Guide

Welcome to the AI Data Labs Beta Testing Program! This guide will help you get started as one of our first design partners.

## 🎯 What You'll Experience

As a beta tester, you'll have access to:
- Early access to AI-powered data infrastructure platform
- Direct feedback channel with our engineering team
- Priority feature requests
- Complimentary usage during beta period
- Exclusive early-adopter benefits at launch

## 📋 Beta Program Goals

Our beta program is designed to:
1. **Validate core value propositions** - Does AI truly make data infrastructure easier?
2. **Identify edge cases** - Find real-world scenarios we haven't considered
3. **Improve user experience** - Make the platform intuitive and delightful
4. **Stress test infrastructure** - Ensure reliability under real workloads
5. **Gather feature requests** - Shape our product roadmap

## 🚀 Getting Started

### Step 1: Account Setup

**Within 24 hours of acceptance:**

1. Check your email for beta account credentials
2. Log in at [https://beta.aidatalabs.ai](https://beta.aidatalabs.ai)
3. Complete your profile:
   - Company name and industry
   - Team size and roles
   - Primary use cases
   - Technical expertise level

### Step 2: Initial Onboarding Call (30 minutes)

Schedule a video call with our team:
- **Purpose:** Understand your goals, set expectations, answer questions
- **Topics covered:**
  - Platform overview and capabilities
  - Your specific use cases and goals
  - Success metrics for your beta period
  - How to provide feedback
- **Preparation:**
  - Bring your current data stack information
  - Have 1-2 specific problems you want to solve
  - Identify team members who will use the platform

**Book your onboarding call:** [Calendly link] (or email: beta@aidatalabs.ai)

### Step 3: Platform Orientation

**Self-paced (1-2 hours):**

Complete these quick tutorials:
- [ ] [Tutorial 1: Your First Query](#tutorial-1-your-first-query) - 15 minutes
- [ ] [Tutorial 2: Design Your First Platform](#tutorial-2-design-your-first-platform) - 30 minutes
- [ ] [Tutorial 3: Create a Dashboard](#tutorial-3-create-a-dashboard) - 20 minutes
- [ ] [Tutorial 4: Connect Your Data Source](#tutorial-4-connect-your-data-source) - 15 minutes

### Step 4: Connect Your Data

**Choose your integration path:**

**Option A: Upload Sample Data (Quickest)**
- Upload CSV/JSON files (up to 100MB)
- Start exploring immediately
- Great for initial testing and familiarization

**Option B: Connect Your Database (Recommended)**
- PostgreSQL, MySQL, ClickHouse, Snowflake
- Secure connection via SSH tunnel or VPN
- Read-only access recommended for beta

**Option C: API Integration**
- REST or GraphQL endpoints
- Custom data pipelines
- Best for streaming data or custom sources

### Step 5: Define Your Success Metrics

Work with your team to define what success looks like:

**Technical Metrics:**
- [ ] Data successfully connected
- [ ] Queries running successfully
- [ ] Dashboards rendering correctly
- [ ] Performance meets expectations (<1s for 95% of queries)

**Business Metrics:**
- [ ] Time saved on data tasks (hours/week)
- [ ] Insights discovered that weren't available before
- [ ] Team members able to self-serve data
- [ ] Decisions made faster

## 🎓 Tutorials

### Tutorial 1: Your First Query

**Goal:** Experience the power of natural language to SQL

**Steps:**

1. Navigate to the **Query** tab in the dashboard
2. You'll see sample data already loaded (e-commerce example)
3. Type a question in natural language:
   ```
   Show me the top 10 products by revenue last month
   ```
4. Watch as our Query Agent:
   - Translates to SQL automatically
   - Runs the query against ClickHouse
   - Displays results in a table
   - Generates a visualization

**Try these queries:**
- "What's our total revenue by month?"
- "Which countries have the most customers?"
- "Show me customer acquisition trends over time"

**Expected Outcome:** You see how easy it is to get answers from data without writing SQL.

---

### Tutorial 2: Design Your First Platform

**Goal:** See AI design a complete data platform from scratch

**Steps:**

1. Navigate to **Platform Designer**
2. Describe your requirements:
   ```
   I need a SaaS analytics platform with:
   - User activity tracking
   - Subscription metrics (MRR, churn, LTV)
   - Feature usage analytics
   - Cohort analysis
   ```
3. Our Platform Designer Agent will:
   - Generate an optimal schema
   - Recommend ClickHouse configuration
   - Suggest data models
   - Create dashboard templates

4. Review and customize:
   - Adjust data types and relationships
   - Add custom fields
   - Rename tables to match your terminology

5. Click **Deploy** to provision infrastructure

**Expected Outcome:** You have a complete data platform designed and deployed in minutes, not weeks.

---

### Tutorial 3: Create a Dashboard

**Goal:** Build a beautiful, interactive dashboard

**Steps:**

1. Navigate to **Dashboards** → **Create New**
2. Choose a template or start blank
3. Add widgets:
   - **Chart Widget:** Select a query or create one
   - **Metric Widget:** Show key KPIs
   - **Table Widget:** Display detailed data
4. Customize each widget:
   - Chart type (line, bar, pie, etc.)
   - Filters and date ranges
   - Colors and styling
5. Arrange and resize widgets
6. Save and share with your team

**Example Dashboard Ideas:**
- Executive Overview (MRR, churn, user growth)
- Product Performance (feature usage, engagement)
- Customer Health (NPS, support tickets, renewals)
- Marketing Campaigns (ROI, conversion, attribution)

**Expected Outcome:** You have a polished dashboard ready for daily use.

---

### Tutorial 4: Connect Your Data Source

**Goal:** Integrate your real data

**Steps:**

1. Navigate to **Data Sources** → **Add New**
2. Choose your source type:
   - **Database:** Enter connection details (host, port, database, credentials)
   - **File:** Upload CSV/JSON/Parquet
   - **API:** Configure endpoint and authentication

3. For databases:
   - Use read-only credentials (recommended)
   - Configure connection pooling
   - Set up SSH tunnel if required
   - Test connection

4. For files:
   - Upload via drag-and-drop
   - Preview and validate
   - Map columns to data types

5. For APIs:
   - Define endpoint URL
   - Configure authentication (API key, OAuth)
   - Set up polling schedule

6. Verify data:
   - Browse data preview
   - Run sample queries
   - Check data quality

**Expected Outcome:** Your real data is flowing into the platform and ready for analysis.

## 📊 Beta Testing Checklist

Use this checklist to track your progress:

### Week 1: Onboarding & Exploration
- [ ] Complete account setup
- [ ] Attend onboarding call
- [ ] Finish all 4 tutorials
- [ ] Connect at least one data source
- [ ] Create your first custom query
- [ ] Build your first dashboard

### Week 2: Integration & Usage
- [ ] Connect all primary data sources
- [ ] Create 3+ dashboards for different use cases
- [ ] Share dashboards with 2+ team members
- [ ] Run 10+ unique queries
- [ ] Use Platform Designer for a new project

### Week 3: Stress Testing
- [ ] Run complex queries on large datasets
- [ ] Test concurrent users (3+ simultaneous)
- [ ] Upload large files (50MB+)
- [ ] Test all integration types (database, file, API)
- [ ] Verify performance benchmarks

### Week 4: Feedback & Evaluation
- [ ] Document all bugs encountered
- [ ] List all feature requests
- [ ] Provide UX feedback
- [ ] Share success stories and wins
- [ ] Complete beta evaluation survey

## 🐛 Reporting Bugs & Issues

### How to Report

**For critical issues (platform down, data loss):**
- Email: urgent@aidatalabs.ai
- Slack: #beta-urgent channel
- Response time: < 2 hours

**For bugs and issues:**
- Use in-app feedback button (top right)
- Tag with: `bug`, `severity: low|medium|high`
- Include:
  - Steps to reproduce
  - Expected vs actual behavior
  - Screenshots/videos
  - Browser and device info

**For feature requests:**
- Use in-app feedback button
- Tag with: `feature-request`
- Describe:
  - Problem you're trying to solve
  - Why current solution doesn't work
  - Ideal solution

### Bug Report Template

```
**Title:** [Brief description]

**Severity:** Low | Medium | High | Critical

**Steps to Reproduce:**
1. Go to...
2. Click on...
3. Scroll to...
4. See error

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happens]

**Environment:**
- Browser: [Chrome/Firefox/Safari version]
- OS: [Windows/Mac/Linux]
- Screen size: [resolution]
- Data source type: [PostgreSQL/CSV/etc]

**Screenshots:**
[Paste screenshots or describe]

**Additional Context:**
[Any other relevant information]
```

## 💡 Feature Requests

We want to build what you need! Share your ideas:

**Format:**
1. **Problem:** What are you trying to achieve?
2. **Current Solution:** How do you solve it now?
3. **Proposed Solution:** What would you like us to build?
4. **Priority:** Must have | Nice to have | Future

**Examples:**

```
**Problem:** I need to schedule reports to run automatically every Monday morning.

**Current Solution:** I manually run queries and export to PDF, then email stakeholders.

**Proposed Solution:** Add a "Schedule Report" feature that allows setting frequency, recipients, and format.

**Priority:** Must have
```

## 📈 Providing Feedback

### Weekly Check-ins

Every week, we'll send a brief survey:
- Platform usage statistics
- Satisfaction rating (1-10)
- Top 3 wins this week
- Top 3 frustrations
- Feature request prioritization

### Feedback Channels

- **In-app feedback:** Click the 💬 button (top right)
- **Email:** beta@aidatalabs.ai
- **Slack:** #beta-testers channel
- **Scheduled calls:** Weekly 30-min sync (optional)

### What Feedback We Value Most

1. **Real-world use cases** - How are you actually using it?
2. **Pain points** - What's frustrating or confusing?
3. **Success stories** - What delighted you?
4. **Missing features** - What would make it 10x better?
5. **Comparison** - How does it compare to your current solution?

## 🎁 Beta Benefits

### During Beta
- Free unlimited usage
- Priority support (24h response SLA)
- Direct access to engineering team
- Influence on product roadmap

### At Launch
- Founding member discount (20% off first year)
- Exclusive beta-only features
- "Founding Beta Tester" badge on your profile
- Early access to all new features
- Case study opportunity (if interested)

## 🤝 Beta Tester Responsibilities

### Commitments

As a beta tester, we ask you to:
1. **Use the platform actively** - At least 2-3 hours per week
2. **Provide feedback weekly** - Bugs, features, suggestions
3. **Test new features** - We'll ship updates weekly
4. **Be patient** - Things will break, that's why we're in beta!
5. **Keep confidential** - Don't share screenshots or details publicly

### Code of Conduct

- Be respectful and constructive in feedback
- Test in good faith (don't try to break things maliciously)
- Protect your data (don't upload sensitive PII)
- Communicate promptly if you need to pause or exit the program

## 📞 Support & Communication

### Support Channels

- **Urgent Issues:** urgent@aidatalabs.ai (2h response)
- **General Questions:** beta@aidatalabs.ai (24h response)
- **Slack Community:** #beta-testers (community support)
- **Video Calls:** Book via [Calendly link]

### Office Hours

**Weekly Office Hours (Thursdays, 2-3 PM UTC):**
- Drop-in Q&A sessions
- No appointment needed
- Discuss challenges, share ideas, get help

### Updates

We'll communicate via:
- Email (weekly digest)
- In-app notifications (feature releases)
- Slack (announcements and community)

## 📅 Timeline

### Beta Duration: 4 Weeks

**Week 1 (March 23-29):** Onboarding & Exploration
- Account setup and tutorials
- Initial data connection
- First queries and dashboards

**Week 2 (March 30 - April 5):** Integration & Usage
- Connect all data sources
- Build production dashboards
- Onboard team members

**Week 3 (April 6-12):** Stress Testing
- Push the limits
- Test edge cases
- Performance validation

**Week 4 (April 13-19):** Feedback & Wrap-up
- Comprehensive feedback
- Final surveys
- Transition planning

**Launch Target:** May 2026

## 🎉 Success Stories

We'd love to hear about your wins! Share:

- Time saved on data tasks
- New insights discovered
- Decisions made faster
- Team empowerment
- Business impact

With your permission, we may feature your story in:
- Case studies
- Blog posts
- Marketing materials
- Conference talks

## ❓ Frequently Asked Questions

**Q: Is my data secure during beta?**
A: Yes! We use enterprise-grade encryption (AES-256), SOC 2 Type II compliant infrastructure, and GDPR-compliant data handling. Your data is never shared or sold.

**Q: What happens to my data after beta?**
A: You can export all data at any time. We offer a seamless migration path to our production platform at launch.

**Q: Can I invite team members?**
A: Yes! During beta, you can invite up to 5 team members at no additional cost.

**Q: What if I find a critical bug?**
A: Report it immediately via urgent@aidatalabs.ai or Slack #beta-urgent. We respond within 2 hours and prioritize critical issues.

**Q: How often will you update the platform?**
A: We ship updates every week, typically on Mondays. We'll announce new features in advance.

**Q: Can I use it for production workloads?**
A: Beta is for testing and evaluation. We recommend using a copy of your data, not production data, during beta.

**Q: What's included in the free beta usage?**
A: Unlimited queries, unlimited storage, all features, priority support. There are no limits during beta.

**Q: What happens after beta ends?**
A: You'll have the option to:
- Convert to a paid plan (20% founding member discount)
- Export your data and discontinue
- Continue on a free tier (limited features)

## 🚀 Ready to Get Started?

Complete these steps now:

1. [ ] Log in to your beta account
2. [ ] Schedule your onboarding call: [Calendly link]
3. [ ] Join the Slack community: [Invite link]
4. [ ] Save this guide for reference

**Questions?** Reach out: beta@aidatalabs.ai

---

**Last Updated:** March 20, 2026
**Beta Coordinator:** duyetbot
**Organization:** Duet Company
