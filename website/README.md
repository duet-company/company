# AI Data Labs Website

Simple static website for AI Data Labs, managed via markdown.

## 📝 Content Management

All content is managed in the `content/` directory as markdown files:

- `about.md` - About page
- `features.md` - Features page
- `pricing.md` - Pricing page
- `contact.md` - Contact page

## 🚀 Build

```bash
cd website
python3 build.py
```

This generates static HTML in the `build/` directory.

## 🔧 Customization

To add a new page:

1. Create a markdown file in `content/` (e.g., `new-page.md`)
2. Add it to the `pages` dictionary in `build.py`
3. Run `python3 build.py`
4. Commit and push

## 📦 Deployment

This site is deployed to GitHub Pages.

**URL:** https://duet-company.github.io/website/ (or configure custom domain)

### GitHub Pages Setup

1. Go to repository settings
2. Scroll to "Pages"
3. Source: Deploy from a branch
4. Branch: `main`, folder: `/docs` or `/website/build`
5. Save

## 🎨 Styling

Edit the CSS in `index.html` or create a separate `style.css` file.

## 🤖 Features

- ✅ Simple static HTML (no build tools required)
- ✅ Markdown content management
- ✅ Fast build (Python script)
- ✅ GitHub Pages compatible
- ✅ Responsive design
- ✅ Dark theme

---

Built with ❤️ for AI Data Labs
