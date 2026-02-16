#!/usr/bin/env python3
"""
Simple static site builder for AI Data Labs website.
Reads markdown files and generates static HTML.
"""

import os
import re
from pathlib import Path
from datetime import datetime

def parse_markdown(content):
    """Parse markdown and convert to HTML."""
    html = content
    # Headers
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    # Bold
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    # Italic
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    # Links
    html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)
    # Code
    html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
    # Line breaks
    html = html.replace('\n\n', '</p><p>')
    html = '<p>' + html + '</p>'
    return html

def read_markdown_file(path):
    """Read a markdown file and extract metadata."""
    with open(path, 'r') as f:
        content = f.read()

    # Extract metadata (YAML frontmatter style)
    metadata = {}
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            metadata_str = parts[1]
            content = parts[2]
            for line in metadata_str.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()

    return metadata, content

def generate_site():
    """Generate the static site."""
    website_dir = Path(__file__).parent
    output_dir = Path(__file__).parent.parent / 'docs'
    content_dir = website_dir / 'content'

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    # Copy index.html
    index_html = website_dir / 'index.html'
    if index_html.exists():
        import shutil
        shutil.copy(index_html, output_dir / 'index.html')
        print(f"✓ Copied index.html")

    # Process content files
    content_dir.mkdir(exist_ok=True)

    # Create simple pages from markdown
    pages = {
        'about.md': 'about.html',
        'features.md': 'features.html',
        'pricing.md': 'pricing.html',
        'contact.md': 'contact.html',
    }

    for md_file, html_file in pages.items():
        md_path = content_dir / md_file
        if md_path.exists():
            metadata, content = read_markdown_file(md_path)
            html_content = parse_markdown(content)

            # Create page template
            page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata.get('title', 'AI Data Labs')}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: #0a0a0a; color: #ffffff; line-height: 1.6; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 2rem 20px; }}
        header {{ background: #111; padding: 1rem 0; border-bottom: 1px solid #333; }}
        nav {{ display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ font-size: 1.25rem; font-weight: 700; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .nav-links a {{ color: #9ca3af; text-decoration: none; margin-left: 2rem; }}
        .nav-links a:hover {{ color: #ffffff; }}
        h1 {{ font-size: 2.5rem; margin-bottom: 1rem; }}
        h2 {{ font-size: 1.75rem; margin: 2rem 0 1rem; }}
        h3 {{ font-size: 1.25rem; margin: 1.5rem 0 0.75rem; }}
        p {{ color: #9ca3af; margin-bottom: 1rem; }}
        a {{ color: #6366f1; }}
        code {{ background: #1f2937; padding: 0.2rem 0.4rem; border-radius: 4px; }}
    </style>
</head>
<body>
    <header>
        <div class="container" style="padding: 0 20px;">
            <nav>
                <div class="logo">AI Data Labs</div>
                <div class="nav-links">
                    <a href="/">Home</a>
                    <a href="/features.html">Features</a>
                    <a href="/pricing.html">Pricing</a>
                    <a href="https://github.com/duet-company/company">GitHub</a>
                </div>
            </nav>
        </div>
    </header>
    <main class="container">
        {html_content}
    </main>
    <footer style="background: #111; padding: 2rem 0; text-align: center; margin-top: 3rem; border-top: 1px solid #333;">
        <p style="color: #9ca3af;">&copy; 2026 Duet Company. AI Data Labs. All rights reserved.</p>
    </footer>
</body>
</html>"""

            with open(output_dir / html_file, 'w') as f:
                f.write(page_html)
            print(f"✓ Generated {html_file}")

    print(f"\n✓ Site built to {output_dir}")
    print(f"  Files: {len(list(output_dir.glob('*.html')))}")

if __name__ == '__main__':
    generate_site()
