# Frontend Dashboard

AI Data Labs - Modern React dashboard built with Next.js 14, TypeScript, and Tailwind CSS + Modern CSS 2025 patterns.

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS
- **Modern CSS 2025** - Advanced patterns (OKLCH, nesting, container queries, etc.)
- **@tanstack/react-query** - Data fetching and caching
- **Biome** - Fast linter and formatter

## Features

- ✅ OKLCH color system for perceptually uniform colors
- ✅ Native CSS nesting (no preprocessor needed)
- ✅ Container queries for responsive components
- ✅ `:has()`, `:is()`, `:where()` modern selectors
- ✅ `text-box: trim` for optical centering
- ✅ `color-mix()` for dynamic color blending
- ✅ Independent transforms (`translate`, `rotate`, `scale`)
- ✅ `@starting-style` for entry animations
- ✅ Smooth height transitions without JS
- ✅ Semantic HTML components
- ✅ Dark mode via `color-scheme` and `light-dark()`
- ✅ Accessibility-first (ARIA roles, :focus-visible)
- ✅ Reduced motion support

## Getting Started

```bash
# Install dependencies
bun install

# Run development server
bun run dev

# Build for production
bun run build

# Start production server
bun run start

# Lint code
bun run lint

# Format code
bun run format

# Type check
bun run typecheck
```

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── (dashboard)/       # Dashboard pages (grouped route)
│   │   ├── layout.tsx     # Dashboard layout with sidebar
│   │   └── page.tsx       # Dashboard home page
│   ├── globals.css        # Modern CSS patterns & utilities
│   └── layout.tsx         # Root layout
├── components/            # Reusable components
│   ├── Card.tsx          # Card component with hover effects
│   ├── Button.tsx        # Modern button with variants
│   ├── Badge.tsx         # Badge component
│   └── Select.tsx        # Accessible select dropdown
├── tailwind.config.js    # Tailwind configuration
├── postcss.config.js     # PostCSS configuration
├── tsconfig.json         # TypeScript configuration
├── next.config.js        # Next.js configuration
└── package.json          # Dependencies and scripts
```

## Modern CSS Patterns Used

### Color System
```css
:root {
  --color-bg: oklch(98% 0.005 85); /* Light mode */
  --color-accent: oklch(0.55 0.2 264);
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: oklch(15% 0.03 250); /* Dark mode */
  }
}
```

### Native Nesting
```css
.card {
  padding: 1.5rem;

  &:hover {
    border-color: var(--color-accent);
  }

  h3 {
    font-size: 1rem;
  }
}
```

### Container Queries
```css
.container-query {
  container-type: inline-size;
}

@container (max-width: 640px) {
  .stack-mobile {
    flex-direction: column;
  }
}
```

### Independent Transforms
```css
.btn:hover {
  translate: 0 -2px;
}
```

### Smooth Height Animation
```css
.accordion {
  height: 0;
  overflow: hidden;
  transition: height 0.3s ease;
}

.accordion.open {
  height: auto;
}
```

## Browser Support

- Chrome/Edge 119+
- Firefox 110+
- Safari 16.4+
- Modern mobile browsers

Some modern CSS features require latest browser versions. See [Can I Use](https://caniuse.com/) for specific features.

## Performance

- ✅ Server-side rendering with Next.js
- ✅ Static generation where possible
- ✅ Minimal JavaScript bundle
- ✅ Optimized CSS with modern features
- ✅ No unnecessary re-renders

## Development

### Adding New Components

1. Create component in `components/` directory
2. Use `'use client'` directive if interactive
3. Export as default or named export
4. Use modern CSS utilities from `globals.css`
5. Add TypeScript types

### Styling Guidelines

- Use CSS custom properties from `:root`
- Prefer `@layer` structure (base, components, utilities)
- Use OKLCH colors for new colors
- Use logical properties (`margin-inline`, `padding-block`)
- Use native nesting for component styles
- Follow accessibility best practices

## Deployment

This frontend is designed to be deployed as a standalone application or integrated into the monorepo.

```bash
# Build
bun run build

# Output in .next/ directory
```

## Learn More

- [Modern CSS Code Snippets](https://modern-css.com/)
- [Oat UI Library](https://oat.ink/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [CSS Nesting](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Selectors/Nesting_selector)

---

Built by **duyetbot** with modern CSS 2025 patterns 🤖
