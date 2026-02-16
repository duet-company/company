# Marketing Skill

Marketing, branding, and go-to-market strategy for Duet Company.

## 🎯 Purpose

Handles marketing operations, brand management, content creation, social media management, and go-to-market strategy for AI Data Labs platform.

## 🚀 Usage

```bash
# Via OpenClaw
@duyetbot Create a marketing campaign for MVP launch

# Direct invocation
marketing-skill "Generate launch announcement for social media"
```

## 📚 Dependencies

- Social media APIs (Twitter/X, LinkedIn, Reddit, HackerNews)
- Content management system
- Blog platform integration
- Email marketing tools
- LLM provider (Claude, GPT-4, or GLM-5)
- Analytics (website traffic, social engagement)

## 🔧 Configuration

### Environment Variables

```bash
# Social Media
TWITTER_API_KEY=***
LINKEDIN_ACCESS_TOKEN=***

REDDIT_CLIENT_ID=***
REDDIT_CLIENT_SECRET=***

HACKERNEWS_API_KEY=***

# Content
BLOG_URL=https://blog.aidatalabs.ai
DOCS_URL=https://docs.aidatalabs.ai
EMAIL_MARKETING_TOOL=***

# Brand
BRAND_NAME=Duet Company
BRAND_TAGLINE=AI-First Data Infrastructure
BRAND_COLORS=#00D4AA, #7C3AED
LOGO_URL=https://aidatalabs.ai/brand/logo.png

# LLM
LLM_PROVIDER=claude|openai|zai
LLM_MODEL=claude-3-opus
LLM_API_KEY=***

# Analytics
GOOGLE_ANALYTICS_ID=***
UMAMI_SITE_ID=***
```

### Skill Configuration

```yaml
marketing:
  brand:
    name: ${BRAND_NAME}
    tagline: ${BRAND_TAGLINE}
    colors:
      primary: ${BRAND_COLORS}
    logo: ${LOGO_URL}
  
  content:
    blog: ${BLOG_URL}
    docs: ${DOCS_URL}
    email: ${EMAIL_MARKETING_TOOL}
  
  social:
    twitter:
      api_key: ${TWITTER_API_KEY}
    linkedin:
      access_token: ${LINKEDIN_ACCESS_TOKEN}
    reddit:
      client_id: ${REDDIT_CLIENT_ID}
      client_secret: ${REDDIT_CLIENT_SECRET}
    hackernews:
      api_key: ${HACKERNEWS_API_KEY}
  
  llm:
    provider: ${LLM_PROVIDER}
    model: ${LLM_MODEL}
    api_key: ${LLM_API_KEY}
  
  analytics:
    google: ${GOOGLE_ANALYTICS_ID}
    umami: ${UMAMI_SITE_ID}
```

## 📖 Examples

### Product Launch Announcement

```markdown
Content Generated:
Excited to announce #AI Data Labs - the first autonomous data infrastructure company!

🚀 What makes us different:
- AI-designed from ground up (not bolted on)
- Hours to production, not months
- 90% reduction in data engineering costs
- Self-healing, self-optimizing infrastructure

🎯 Launching today with:
- Complete AI agent platform (Query, Design, Support, Ops)
- Real-time analytics on ClickHouse
- Natural language interface for everyone

📊 Our mission: Democratize enterprise-grade data analytics

Join us at https://aidatalabs.ai and experience the future of data infrastructure.

#AIDataLabs #DuetCompany #AI #DataEngineering

Platforms:
- Twitter/X (post + reply)
- LinkedIn (article + company page)
- Reddit (multiple subreddits)
- HackerNews (Show HN)

Analytics Tracking:
- UTM parameters: ?utm_source=launch&utm_medium=social&utm_campaign=v1
- Traffic source tracking enabled
- Conversion tracking set up

Metrics:
- Twitter impressions and engagement
- LinkedIn views and clicks
- Reddit upvotes and comments
- Website visits and signups
- Social media reach (combined)
```

### Blog Post Promotion

```markdown
Content Generated:
New on the blog: "Building an AI-First Data Infrastructure Company" 🤖

Read more about our journey from concept to launch: https://blog.aidatalabs.ai/ai-first-data-infrastructure-company

Highlights:
- The vision behind Duet Company
- Technical challenges we solved
- How AI agents enable our approach
- What's next for AI Data Labs

Channels:
- Twitter/X (thread with summary)
- LinkedIn (article post)
- Email newsletter
- Company blog RSS feed
- Documentation site

Call to Action:
"Check out our full technical documentation at https://docs.aidatalabs.ai and our platform at https://aidatalabs.ai"

SEO Optimization:
- Title tags: AI, Data Infrastructure, Company, Startup, Launch
- Meta description: Max 160 characters with keywords
- Alt text: AI Data Labs - Autonomous Data Platform
- Featured image: Platform screenshot
- Open graph tags: website, article

Metrics:
- Blog views and read time
- CTR on documentation links
- Newsletter signups from blog post
- Social media clicks to blog
```

### Email Marketing Campaign

```markdown
Campaign: "Beta User Invitation - Sprint 1"

Subject Line:
"🎉 You're Invited to Beta AI Data Labs!"

Content Generated:
Hi [Name],

We're excited to invite you to be one of our first beta users for AI Data Labs!

What is AI Data Labs?
--------------------
The world's first AI-first data infrastructure company. Our autonomous AI agents design, deploy, and manage scalable data platforms in hours, not months.

What You'll Get:
- 🚀 Real-time analytics platform setup in 1 hour
- 🤖 Natural language to SQL queries (just ask questions!)
- 📊 Dashboards and reports generated automatically
- 🔧 Infrastructure managed by AI agents
- 24/7 AI-powered support

As a Beta User:
- ✅ Free access to full platform
- 📣 Early access to all features
- 🗣 Direct input into product roadmap
- 💬 Priority support and feedback

What We Need From You:
- 📝 30 minutes of your time for initial onboarding call
- 📊 Access to your current data infrastructure for migration testing
- 💡 Honest feedback on what works and what doesn't

Ready to start?
[Link: Sign Up for Beta] (with UTM)
[Link: Read Documentation] (with UTM)
[Link: Schedule Call] (calendar link)

Beta Period: 8 weeks
Platform: https://beta.aidatalabs.ai

Let's build the future of data infrastructure together!

Best,
The AI Data Labs Team

Email Configuration:
- From: hello@aidatalabs.ai
- Reply-to: [beta-user-email]
- Platform: [choose email tool]
- Template: Beta Invitation
- Tracking: Enabled with UTM parameters

Analytics:
- Email open rate
- Click-through rate (CTR)
- Sign-up conversion rate
- Time to sign-up
- Source tracking (email, social, direct)

Metrics:
- Email sent: [number]
- Email opened: [number]
- Clicks: [number]
- Sign-ups: [number]
- Conversion rate: [percentage]

```

## 🐛 Troubleshooting

### Issue: Social media post fails

**Possible causes:**
- API rate limit exceeded
- Invalid API credentials
- Content policy violation
- Network connectivity issue

**Solutions:**
1. Check API status: `marketing-skill --check-social-status`
2. Verify credentials: Review environment variables
3. Check content guidelines: Ensure compliance with platform policies
4. Retry with exponential backoff: Built into skill

### Issue: Email not delivered

**Possible causes:**
- Invalid email address
- Email provider blocking
- Spam filter triggered
- Daily send limit exceeded

**Solutions:**
1. Verify email: Use tool to validate format
2. Check sender reputation: `marketing-skill --check-sender-rep`
3. Review content: Remove spam triggers
4. Use alternative sender if needed

### Issue: Low engagement on posts

**Possible causes:**
- Poor content quality
- Bad posting time
- Irrelevant to audience
- No call-to-action
- Poor formatting

**Solutions:**
1. A/B test content: Try different approaches
2. Optimize timing: Use analytics to find best times
3. Improve relevance: Add more value to posts
4. Strong CTA: Clear next steps and benefits
5. Use hashtags strategically: #AI #DataEngineering #Startups

## 📊 Marketing Metrics

### KPIs We Track

| Category | Metric | Target | Current | Status |
|----------|--------|--------|--------|
| Brand Awareness | Social media followers | 1000 Q1 | TBD |
| Content Marketing | Blog subscribers | 500 Q1 | TBD |
| Product Launch | Sign-ups (beta) | 50 Q1 | TBD |
| Website Traffic | Monthly visitors | 5000 Q1 | TBD |
| Email Marketing | Open rate | 25% | TBD |
| Social Engagement | Engagement rate | 3% | TBD |

### Funnel Metrics

```
Awareness → Interest → Consideration → Sign-up → Activation

Metrics:
- Social media reach: 50,000
- Website visitors: 5,000
- Email list: 2,000
- Beta sign-ups: 50
- Activated users: 30
- Paid conversion (post-beta): 10%

Conversion rates:
- Interest → Consideration: 10%
- Consideration → Sign-up: 5%
- Sign-up → Activation: 60%
- Activation → Paid: 33%

Optimization focus: Improve Consideration → Sign-up conversion
```

## 🔗 Integration

- **Blog:** https://github.com/duet-company/blog
- **Docs:** https://github.com/duet-company/docs
- **Website:** https://github.com/duet-company/frontend
- **Social Skills:** Twitter/X API, LinkedIn API

## 📖 References

- [Social Media Marketing Guide](https://github.com/duet-company/playbook/blob/main/marketing/social-media.md)
- [Content Strategy](https://github.com/duet-company/playbook/blob/main/marketing/content-strategy.md)
- [Product Launch](https://github.com/duet-company/vision/blob/main/ROADMAP.md#phase-4-launch-weeks-13-16)
- [Analytics Setup](https://github.com/duet-company/infrastructure/blob/main/analytics/README.md)

---

**Skill Version:** 1.0.0
**Last Updated:** 2026-02-16
**Maintainer:** Duet Company Marketing
