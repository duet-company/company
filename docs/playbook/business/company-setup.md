# Company Setup SOP

This SOP covers the essential business setup tasks for Duet Company: company registration and domain acquisition.

---

## Task 1: Domain Acquisition (aidatalabs.ai)

### Overview
- **Priority:** High - Blocker for website and email setup
- **Estimated Time:** 1-2 hours
- **Status:** 🚧 Ready

### Steps

1. **Choose Registrar**
   - Namecheap.com - Recommended (good .ai pricing, excellent support)
   - Gandi.net - Privacy-focused
   - Google Domains - Simple, but limited TLD support

2. **Check Availability**
   - Visit registrar and search: `aidatalabs.ai`
   - If unavailable, consider alternatives:
     - aidatalabs.com
     - duet-data.ai
     - duetlabs.ai

3. **Purchase Domain**
   - Create account with registrar
   - Purchase domain for 1-5 years (recommended: 5 years for SEO)
   - Enable WHOIS privacy protection
   - Enable auto-renewal
   - Add 2FA to registrar account

4. **Configure DNS**
   - Point to hosting (Cloudflare Workers for now)
   - Add DNS records:
     ```
     A Record: aidatalabs.ai → Cloudflare IP
     CNAME: www → aidatalabs.ai
     MX Records: Configure email service (e.g., Google Workspace, Fastmail)
     ```

5. **Verify Ownership**
   - Use domain verification for:
     - Google Search Console
     - Google Analytics
     - Email services (DKIM, SPF, DMARC)

### Deliverables
- [ ] Domain purchased and configured
- [ ] DNS records set up
- [ ] Ownership verified with Google
- [ ] Email service configured
- [ ] SSL certificate (auto-provisioned by Cloudflare)

### Notes
- .ai domains are expensive ($100-200/year) but essential for AI company branding
- Consider purchasing similar domains to prevent typosquatting (e.g., aidatalabs.com)
- Keep registrar login in secure password manager (e.g., 1Password, Bitwarden)

---

## Task 2: Company Registration (Singapore C-Corp)

### Overview
- **Priority:** High - Legal entity needed for banking, contracts, payments
- **Estimated Time:** 1-2 weeks
- **Status:** 🚧 Open

### Steps

1. **Choose Incorporation Service**
   - Osome.co - Recommended (full-service, affordable, fast)
   - Sleek.com - Modern, tech-friendly
   - FirstBase.io - Good for international founders

2. **Prepare Documents**
   - Company name options (3 choices, in order of preference)
   - Business activity description (e.g., "Software development and data analytics services")
   - Passport copies for all directors
   - Residential address proof for directors
   - Shareholder structure (% for each shareholder)

3. **Submit Application**
   - Complete ACRA (Accounting and Corporate Regulatory Authority) application via service
   - Pay incorporation fees (~SGD 300-400 + service fees)
   - Wait for approval (1-3 business days)

4. **Post-Incorporation**
   - Open corporate bank account (DBS, UOB, OCBC, or Wise for international)
   - Register for GST (only if revenue > SGD 1M/year)
   - Set up company secretary (required in Singapore)
   - Register business address (virtual office options available)

5. **Legal & Compliance**
   - Register for CPF contributions (if hiring local employees)
   - Set up corporate insurance (professional liability)
   - Prepare shareholder agreement
   - Create director resolutions for bank account opening

### Deliverables
- [ ] Company incorporated with ACRA
- [ ] Business Profile (BizFile) obtained
- [ ] Certificate of Incorporation received
- [ ] Corporate bank account opened
- [ ] Company secretary appointed
- [ ] Shareholder agreement drafted
- [ ] Insurance policies in place

### Notes
- Singapore C-Corp is ideal for global operations (low tax, business-friendly)
- Minimum 1 director, 1 shareholder (can be the same person)
- Foreign directors can incorporate remotely, but must visit Singapore for some banks
- Keep all incorporation documents in secure folder (Google Drive company folder)

---

## Task 3: Brand Assets

### Overview
- **Priority:** Medium - Can iterate, but should be done before public launch
- **Estimated Time:** 1-2 weeks
- **Status:** 🚧 Open

### Steps

1. **Logo Design**
   - Hire designer or use AI tools (DALL-E, Midjourney, Looka)
   - Requirements:
     - Simple, scalable (works at 16x16 and 512x512)
     - Color-agnostic (works in light/dark mode)
     - Modern, tech-forward aesthetic
   - Deliverables:
     - SVG source file
     - PNG (512x512, 256x256, 128x128, 64x64, 32x32)
     - Favicon (ICO)

2. **Color Palette**
   - Primary: Deep blue (#1E3A8A) or similar
   - Accent: Electric blue or purple (#8B5CF6)
   - Neutral: Grays (#F3F4F6, #6B7280, #1F2937)
   - Define hex codes and use cases

3. **Typography**
   - Headings: Inter, Geist, or system sans-serif
   - Body: Same as headings (consistent)
   - Code: JetBrains Mono or Fira Code

4. **Design System**
   - Create Figma or Sketch file with:
     - Logo variations
     - Color palette
     - Typography scale
     - Button styles
     - Card components
     - Form inputs
     - Spacing system

5. **Brand Guidelines**
   - Document logo usage rules
   - Define brand voice and tone
   - Create examples of on-brand vs off-brand

### Deliverables
- [ ] Logo files (SVG + PNGs in multiple sizes)
- [ ] Favicon and app icons
- [ ] Color palette defined
- [ ] Typography system defined
- [ ] Figma/Sketch design system
- [ ] Brand guidelines document

### Notes
- Iterate quickly with AI tools for initial concepts
- Consider hiring professional designer for final polish
- Keep brand assets in version control (git)
- Reference existing design systems (shadcn/ui, Vercel, Linear) for inspiration

---

## Priority Order

1. **Domain acquisition** - Blocking for website and email
2. **Company registration** - Blocking for banking and contracts
3. **Brand assets** - Can be iterated, but need for launch

---

## Tools & Services

### Domain & DNS
- Registrar: Namecheap.com or Gandi.net
- DNS: Cloudflare (free, fast, DDoS protection)

### Company Registration
- Service: Osome.co or Sleek.com
- Banking: DBS/OCBC/UOB (Singapore) or Wise (international)
- Secretary: Osome provides as add-on

### Design
- Logo: Looka.com, Midjourney, DALL-E
- Design system: Figma (collaborative, free tier)
- Icons: Lucide, Heroicons, Phosphor

### Document Storage
- Company docs: Google Workspace (Drive, Docs, Sheets)
- Passwords: 1Password Team or Bitwarden

---

## Success Criteria

- Domain: aidatalabs.ai resolves to website, email working
- Company: ACRA registration complete, bank account active
- Brand: Logo and design system ready for website/marketing

---

**Last Updated:** 2026-03-22
**Next Review:** After domain acquisition complete
