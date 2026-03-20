# Billing and Subscriptions Implementation Guide

**Phase:** Phase 4 (Launch) Preparation  
**Target:** Weeks 13-16  
**Purpose:** Define billing infrastructure and subscription management for AI Data Labs

---

## 📋 Overview

This guide covers the implementation of billing, subscription management, and payment processing for the AI Data Labs platform.

---

## 💳 Pricing Tiers

### Starter Plan
- **Price:** $999/month
- **Data:** 1TB/month
- **Users:** 5
- **Features:**
  - Query Agent
  - Basic analytics
  - Email support
  - API access

### Growth Plan
- **Price:** $2,999/month
- **Data:** 10TB/month
- **Users:** 20
- **Features:**
  - Query Agent
  - Platform Designer Agent
  - Priority support
  - Email + chat support
  - Advanced analytics
  - API access

### Enterprise Plan
- **Price:** Custom
- **Data:** Unlimited
- **Users:** Unlimited
- **Features:**
  - All AI agents
  - Dedicated support
  - 24/7 phone support
  - Custom SLA
  - On-premise deployment
  - Custom integrations

---

## 🔧 Technical Implementation

### 1. Payment Processing

**Recommended Provider:** Stripe (or PayPal as backup)

#### Integration Requirements
```python
# Example Stripe integration structure
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Create customer
customer = stripe.Customer.create(
    email=user.email,
    name=user.name,
    metadata={'user_id': user.id}
)

# Create subscription
subscription = stripe.Subscription.create(
    customer=customer.id,
    items=[{
        'price': price_id,  # Starter/Growth/Enterprise
    }],
    payment_behavior='default_incomplete',
    payment_settings={'save_default_payment_method': 'on_subscription'},
    expand=['latest_invoice.payment_intent'],
    metadata={
        'user_id': user.id,
        'tier': 'starter'  # or 'growth', 'enterprise'
    }
)
```

#### Billing Webhooks
Implement webhook handlers for:
- `checkout.session.completed` - Successful payment
- `invoice.paid` - Invoice paid
- `invoice.payment_failed` - Payment failed
- `customer.subscription.deleted` - Subscription cancelled
- `customer.subscription.updated` - Plan changed

### 2. Database Schema

```sql
-- Subscriptions table
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    stripe_subscription_id VARCHAR(255) UNIQUE NOT NULL,
    stripe_customer_id VARCHAR(255) UNIQUE NOT NULL,
    tier VARCHAR(50) NOT NULL CHECK (tier IN ('starter', 'growth', 'enterprise')),
    status VARCHAR(50) NOT NULL CHECK (status IN ('active', 'past_due', 'canceled', 'trialing')),
    current_period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    current_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Usage tracking table
CREATE TABLE usage_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id UUID NOT NULL REFERENCES subscriptions(id),
    data_processed_gb NUMERIC NOT NULL,
    query_count INTEGER NOT NULL,
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Invoices table (sync with Stripe)
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id UUID NOT NULL REFERENCES subscriptions(id),
    stripe_invoice_id VARCHAR(255) UNIQUE NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) NOT NULL,
    due_date TIMESTAMP WITH TIME ZONE,
    paid_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Usage limits table
CREATE TABLE usage_limits (
    tier VARCHAR(50) PRIMARY KEY,
    data_limit_gb INTEGER NOT NULL,
    user_limit INTEGER NOT NULL,
    features JSONB NOT NULL
);

INSERT INTO usage_limits (tier, data_limit_gb, user_limit, features) VALUES
('starter', 1024, 5, '["query_agent", "basic_analytics", "email_support", "api_access"]'::jsonb),
('growth', 10240, 20, '["query_agent", "platform_designer_agent", "priority_support", "email_chat_support", "advanced_analytics", "api_access"]'::jsonb),
('enterprise', -1, -1, '["all_agents", "dedicated_support", "24_7_phone_support", "custom_sla", "on_premise", "custom_integrations", "api_access"]'::jsonb);
```

### 3. API Endpoints

#### Subscription Management
```python
# Get current subscription
GET /api/v1/subscriptions/current

# Update subscription (change tier)
POST /api/v1/subscriptions/{id}/upgrade
POST /api/v1/subscriptions/{id}/downgrade

# Cancel subscription
POST /api/v1/subscriptions/{id}/cancel

# Resume subscription
POST /api/v1/subscriptions/{id}/resume

# Get usage statistics
GET /api/v1/subscriptions/{id}/usage

# Get payment history
GET /api/v1/subscriptions/{id}/invoices
```

#### Usage Enforcement
```python
# Middleware to check usage limits
async def check_usage_limits(user: User, action: str):
    subscription = await get_user_subscription(user.id)
    limits = await get_tier_limits(subscription.tier)
    
    if subscription.tier == 'enterprise':
        return True  # Enterprise has unlimited
    
    usage = await get_current_usage(subscription.id)
    
    if action == 'query':
        if usage.query_count >= MAX_DAILY_QUERIES[subscription.tier]:
            raise UsageLimitExceeded("Query limit exceeded")
    
    if action == 'ingest':
        if usage.data_processed_gb >= limits.data_limit_gb:
            raise UsageLimitExceeded("Data limit exceeded")
    
    if action == 'add_user':
        if usage.user_count >= limits.user_limit:
            raise UsageLimitExceeded("User limit exceeded")
    
    return True
```

### 4. Billing Features

#### Free Trial
- 14-day free trial for all tiers
- No credit card required for trial
- Automatic conversion to paid subscription after trial
- Trial extension available (1-7 days) via support request

#### Payment Methods
- Credit cards (Visa, MasterCard, Amex)
- Debit cards
-ACH transfer (Enterprise only)
- Invoice with Net-30 terms (Enterprise only)

#### Billing Cycle
- Monthly billing (default)
- Annual billing with 10% discount
- Pro-rated billing for mid-cycle changes

#### Invoice Management
- Automatic invoice generation
- PDF invoice download
- Custom invoicing (Enterprise)
- Multi-currency support (USD, EUR, GBP, JPY)

---

## 🚨 Usage Monitoring

### 1. Real-Time Tracking
```python
# Track data ingestion
async def track_data_ingestion(user_id: UUID, data_size_gb: float):
    subscription = await get_active_subscription(user_id)
    
    await execute_query("""
        INSERT INTO usage_tracking (subscription_id, data_processed_gb, query_count, period_start, period_end)
        VALUES ($1, $2, 0, 
                date_trunc('month', NOW()), 
                date_trunc('month', NOW()) + INTERVAL '1 month')
        ON CONFLICT (subscription_id, period_start)
        DO UPDATE SET data_processed_gb = usage_tracking.data_processed_gb + $2
    """, subscription.id, data_size_gb)
    
    # Check if limit exceeded
    usage = await get_current_usage(subscription.id)
    limits = await get_tier_limits(subscription.tier)
    
    if usage.data_processed_gb >= limits.data_limit_gb * 0.9:
        await send_usage_alert(user_id, "Data limit 90% used")
    
    if usage.data_processed_gb >= limits.data_limit_gb:
        await enforce_data_limit(subscription.id)
```

### 2. Alerts and Notifications
- 80% usage warning email
- 90% usage warning email
- 100% usage enforcement (block new data ingestion)
- Overages: Allow with $0.10/GB additional charge (Enterprise only)

---

## 🔄 Subscription Lifecycle

### 1. Sign Up Flow
1. User creates account
2. Select plan (Starter/Growth/Enterprise)
3. Enter billing details (or start trial)
4. Create Stripe customer
5. Create subscription
6. Enable platform access

### 2. Plan Upgrade Flow
1. User requests upgrade
2. Prorate billing for current month
3. Update Stripe subscription
4. Update database tier
5. Apply new limits immediately
6. Send confirmation email

### 3. Plan Downgrade Flow
1. User requests downgrade
2. Effective at next billing period
3. Schedule Stripe subscription update
4. Notify user of scheduled change
5. Apply new limits on renewal

### 4. Cancellation Flow
1. User requests cancellation
2. Confirm cancellation intent
3. Set `cancel_at_period_end = TRUE`
4. Continue access until period end
5. Graceful shutdown (7-day data retention)
6. Send confirmation email

---

## 📊 Revenue Recognition

### 1. MRR Tracking
- Monthly Recurring Revenue (MRR)
- Annual Recurring Revenue (ARR)
- Expansion MRR (upgrades)
- Contraction MRR (downgrades/cancellations)
- Churn MRR

### 2. Metrics to Track
- Customer Acquisition Cost (CAC)
- Customer Lifetime Value (LTV)
- LTV:CAC Ratio (target >3:1)
- Monthly Churn Rate (target <5%)
- Net Revenue Retention (target >120%)
- Revenue per Customer

---

## 🔒 Security and Compliance

### 1. PCI DSS Compliance
- Never store full credit card numbers
- Use Stripe.js for secure card entry
- Tokenization via Stripe API
- Annual PCI compliance audit

### 2. Data Privacy
- GDPR-compliant billing practices
- Data retention policy
- Customer data export on cancellation
- Right to be forgotten

### 3. Fraud Detection
- Stripe Radar integration
- IP-based velocity checks
- Email verification for new accounts
- Suspicious activity alerts

---

## 📞 Support and Escalations

### 1. Billing Support
- Email: billing@aidatalabs.ai
- Chat support (Growth and Enterprise)
- Phone support (Enterprise only)
- Response SLA:
  - Starter: 24 hours
  - Growth: 12 hours
  - Enterprise: 4 hours

### 2. Common Issues
- Payment failed: Retry 3x, then suspend
- Refund request: Review within 48 hours
- Billing dispute: Contact Stripe, support customer
- Plan change: Immediate for upgrade, next cycle for downgrade

### 3. Refund Policy
- No refunds for partial months
- Full refund within 7 days of signup
- Prorated refund for annual plans
- Exceptions handled case-by-case

---

## 🚀 Launch Checklist

### Pre-Launch
- [ ] Stripe account configured and verified
- [ ] All price tiers created in Stripe
- [ ] Webhook endpoints implemented and tested
- [ ] Database schema created and migrated
- [ ] API endpoints implemented and tested
- [ ] Usage tracking middleware integrated
- [ ] Email templates created
- [ ] Billing support channel established

### Launch Day
- [ ] Enable billing for new signups
- [ ] Monitor first payment processing
- [ ] Verify webhook delivery
- [ ] Check usage tracking accuracy
- [ ] Support team on standby

### Post-Launch (Days 1-7)
- [ ] Monitor payment success rate (>95%)
- [ ] Track conversion from trial to paid
- [ ] Address billing support tickets
- [ ] Review usage patterns
- [ ] Optimize onboarding flow

---

## 📈 Success Metrics

### Week 1
- 50 new signups (including trials)
- 30% trial-to-paid conversion
- 95% payment success rate
- <5% billing support tickets

### Month 1
- 200 new signups
- 40% trial-to-paid conversion
- 98% payment success rate
- <3% churn rate
- $10,000 MRR

### Quarter 1
- 1,000 total customers
- 50% trial-to-paid conversion
- 99% payment success rate
- <2% churn rate
- $100,000 MRR
- $20,000 Expansion MRR

---

## 🔗 Integration Points

### Existing Services
- **User Service:** Sync customer data
- **Query Service:** Enforce query limits
- **Ingestion Service:** Enforce data limits
- **Notification Service:** Send billing alerts
- **Monitoring Service:** Track billing KPIs

### External Services
- **Stripe:** Payment processing
- **Email Service:** Billing notifications
- **Support Service:** Billing support tickets

---

## 📚 Additional Resources

- [Stripe Documentation](https://stripe.com/docs)
- [Billing Best Practices](https://stripe.com/docs/billing)
- [PCI DSS Compliance Guide](https://www.pcisecuritystandards.org/)
- [GDPR Compliance Checklist](https://gdpr.eu/checklist/)

---

**Last Updated:** 2026-03-20  
**Status:** Draft - Ready for Implementation  
**Next Steps:** Review with team, begin implementation after domain acquisition
