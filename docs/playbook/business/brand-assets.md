# AI Data Labs - Brand Assets

**Version:** 1.0
**Created:** 2026-03-22
**Status:** 🚧 In Progress

---

## Logo Design

### Concept

**Visual Metaphor:**
- Abstract representation of data transformation and AI intelligence
- Clean, geometric shapes suggesting flow and connection
- Minimalist mark that works at all sizes (16px to 512px)

**Design Principles:**
1. **Simplicity:** No more than 3 distinct elements
2. **Scalability:** Must be recognizable at favicon size (16x16)
3. **Versatility:** Works in color, grayscale, and single-color
4. **Timelessness:** Avoid trendy gradients or effects
5. **Tech-forward:** Subtle nod to AI/neural networks without clichés

### Logo Brief (for Designer/AI Tool)

**Primary Mark:**
- Geometric symbol + wordmark combination
- Symbol represents: data + AI + transformation
- Abstract hexagon or network pattern suggestion
- Clean lines, negative space usage

**Wordmark:**
- "AI Data Labs" in sans-serif font
- Weight: Medium (500-600)
- Spacing: Slightly expanded for modern feel
- Alignment: Left-aligned with symbol

**Color Variations:**
- Full color: Primary blue + accent
- Single color: Dark gray (#1F2937) for print
- Light mode: Full color
- Dark mode: Monochrome or accent-only

### Logo Requirements

**Sizes Needed:**
- SVG (vector source)
- PNG @ 512x512 (large)
- PNG @ 256x256 (medium)
- PNG @ 128x128 (small)
- PNG @ 64x64 (icon)
- PNG @ 32x32 (small icon)
- ICO (favicon)

**File Naming:**
- `logo-primary.svg` - Main logo
- `logo-primary-[size].png` - Raster versions
- `favicon.ico` - 32x32 and 16x16
- `app-icon.png` - 512x512 for app stores

---

## Color Palette

### Primary Colors

**Brand Blue (Primary):**
```
Hex: #1E3A8A
RGB: 30, 58, 138
HSL: 222, 64%, 33%
Usage: Primary brand color, CTAs, headers
```

**Electric Blue (Accent):**
```
Hex: #3B82F6
RGB: 59, 130, 246
HSL: 217, 90%, 60%
Usage: Links, highlights, active states
```

**Purple Accent (Secondary):**
```
Hex: #8B5CF6
RGB: 139, 92, 246
HSL: 258, 53%, 66%
Usage: AI-related features, neural network elements
```

### Neutral Colors

**White (Background):**
```
Hex: #FFFFFF
RGB: 255, 255, 255
Usage: Primary background, cards
```

**Light Gray (Surface):**
```
Hex: #F3F4F6
RGB: 243, 244, 246
Usage: Secondary backgrounds, borders
```

**Gray (Text):**
```
Hex: #6B7280
RGB: 107, 114, 128
Usage: Secondary text, labels
```

**Dark Gray (Heading):**
```
Hex: #1F2937
RGB: 31, 41, 55
Usage: Headings, primary text
```

**Black (High Contrast):**
```
Hex: #000000
RGB: 0, 0, 0
Usage: Highest contrast elements, dark mode base
```

### Semantic Colors

**Success:**
```
Hex: #10B981
Usage: Success states, positive feedback
```

**Warning:**
```
Hex: #F59E0B
Usage: Warnings, caution states
```

**Error:**
```
Hex: #EF4444
Usage: Errors, destructive actions
```

**Info:**
```
Hex: #3B82F6
Usage: Informational messages
```

### Dark Mode Palette

**Background:** #0F172A (Slate 900)
**Surface:** #1E293B (Slate 800)
**Text Primary:** #F8FAFC (Slate 50)
**Text Secondary:** #94A3B8 (Slate 400)

---

## Typography

### Font System

**Primary Font Family:**
```
Family: Inter
Fallback: system-ui, -apple-system, BlinkMacSystemFont, sans-serif
Weights: 400 (Regular), 500 (Medium), 600 (Semibold), 700 (Bold)
```

**Code Font:**
```
Family: JetBrains Mono
Fallback: Fira Code, Consolas, monospace
Weights: 400 (Regular), 500 (Medium)
```

### Type Scale

**Display:**
- H1: 48px / 56px line-height (bold)
- H2: 36px / 44px line-height (semibold)
- H3: 30px / 40px line-height (semibold)

**Body:**
- Large: 18px / 28px line-height (regular)
- Base: 16px / 24px line-height (regular)
- Small: 14px / 20px line-height (regular)

**Caption:**
- Caption: 12px / 16px line-height (medium)

---

## Design System Principles

### Core Values

1. **Clarity Over Cleverness**
   - Content first, design second
   - Clear hierarchy and information architecture
   - Avoid unnecessary decorations

2. **Performance First**
   - Fast load times
   - Optimized assets
   - Minimal dependencies

3. **Accessibility**
   - WCAG AA compliant color contrast (4.5:1)
   - Keyboard navigation
   - Screen reader support

4. **Developer Experience**
   - Consistent patterns
   - Well-documented components
   - Easy to customize

### Spacing System

**Base Unit:** 4px

**Scale:**
- xs: 4px
- sm: 8px
- md: 16px (base spacing)
- lg: 24px
- xl: 32px
- 2xl: 48px
- 3xl: 64px

### Border Radius

**Scale:**
- sm: 4px (buttons, inputs)
- md: 8px (cards, containers)
- lg: 12px (modals, panels)
- xl: 16px (hero sections)
- full: 9999px (pills, tags)

### Shadows

**Elevation Scale:**
- xs: 0 1px 2px rgba(0,0,0,0.05)
- sm: 0 1px 3px rgba(0,0,0,0.1)
- md: 0 4px 6px rgba(0,0,0,0.1)
- lg: 0 10px 15px rgba(0,0,0,0.1)
- xl: 0 20px 25px rgba(0,0,0,0.15)

---

## Component Guidelines

### Buttons

**Primary Button:**
- Background: Brand Blue (#1E3A8A)
- Text: White
- Hover: Darken by 10%
- Radius: 4px
- Padding: 8px 16px (sm), 12px 24px (md)

**Secondary Button:**
- Background: Light Gray (#F3F4F6)
- Text: Dark Gray (#1F2937)
- Border: 1px solid Gray (#E5E7EB)
- Hover: Medium Gray (#E5E7EB)

**Ghost Button:**
- Background: Transparent
- Text: Brand Blue (#1E3A8A)
- Hover: Light Blue (#EFF6FF)

### Cards

**Default:**
- Background: White
- Border: 1px solid Light Gray (#E5E7EB)
- Radius: 8px
- Shadow: sm
- Padding: 24px

**Elevated:**
- Background: White
- Border: None
- Radius: 12px
- Shadow: md
- Padding: 32px

### Inputs

**Default:**
- Background: White
- Border: 1px solid Light Gray (#E5E7EB)
- Radius: 4px
- Padding: 8px 12px
- Focus Border: Brand Blue (#1E3A8A)
- Focus Ring: 0 0 0 3px rgba(30, 58, 138, 0.1)

---

## Brand Voice & Tone

### Personality Traits

1. **Expert but Accessible**
   - We know our stuff, but explain it simply
   - No jargon without explanation
   - Educational, not intimidating

2. **Innovative but Reliable**
   - Cutting-edge technology
   - Proven, stable platform
   - Trustworthy, not experimental

3. **Efficient but Thorough**
   - Get results fast
   - Don't cut corners
   - Quality matters

### Tone Guidelines

**Do:**
- Use active voice
- Be concise and direct
- Explain technical concepts simply
- Show empathy for user challenges

**Don't:**
- Use excessive exclamation points
- Be overly casual or slangy
- Make promises we can't keep
- Use passive voice

### Copy Examples

**Hero:**
- "AI-First Data Infrastructure: Hours to Production, Not Months"

**Subheadline:**
- "Build scalable data platforms in minutes, not months. From schema design to production deployment, AI handles the complexity."

**CTA:**
- "Start Free Trial" / "Get Started" / "Deploy Now"

**Feature Description:**
- "Natural Language Querying: Ask questions in plain English, get SQL queries instantly."

---

## Asset Delivery Checklist

### Logo Files
- [ ] logo-primary.svg (vector source)
- [ ] logo-primary-512.png
- [ ] logo-primary-256.png
- [ ] logo-primary-128.png
- [ ] logo-primary-64.png
- [ ] logo-primary-32.png
- [ ] favicon.ico (32x32 + 16x16)
- [ ] app-icon.png (512x512)

### Documentation
- [x] Brand assets specification (this document)
- [ ] Logo usage guidelines
- [ ] Figma design system file
- [ ] Component library (shadcn/ui based)

### Code Assets
- [ ] CSS variables for colors
- [ ] Tailwind config with brand colors
- [ ] Typography tokens
- [ ] Spacing system implementation

---

## Next Steps

1. **Immediate:**
   - [ ] Generate logo concepts using AI tools
   - [ ] Create SVG logo file
   - [ ] Export raster sizes
   - [ ] Generate favicon

2. **Short-term (Week 1):**
   - [ ] Set up Tailwind config with brand colors
   - [ ] Create base CSS variables
   - [ ] Document logo usage rules

3. **Medium-term (Week 2):**
   - [ ] Build Figma design system
   - [ ] Create component library
   - [ ] Document brand guidelines

4. **Long-term (Week 3+):**
   - [ ] Iterate based on feedback
   - [ ] Refine brand voice
   - [ ] Create brand templates

---

## References & Inspiration

**Design Systems:**
- Vercel Design System
- Linear Design System
- shadcn/ui components

**Color Palettes:**
- Tailwind CSS Blue palette
- Dracula theme (dark mode)
- Nord palette (accessibility-focused)

**Typography:**
- Inter (Google Fonts)
- JetBrains Mono (JetBrains)
- Geist Mono (Vercel)

---

**Last Updated:** 2026-03-22
**Owner:** Duet Company
**Status:** 🚧 In Progress - Logo generation pending
