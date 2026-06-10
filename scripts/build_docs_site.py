#!/usr/bin/env python3
"""Build a simple static docs site from markdown files.

Converts docs/*.md to site/*.html with a minimal CSS stylesheet.
No external dependencies — uses a simple markdown-to-HTML converter.

Usage:
    python scripts/build_docs_site.py --docs docs --output site
"""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path


# Simple markdown to HTML converter (no external deps)
def _md_to_html(text: str) -> str:
    """Convert basic markdown to HTML."""
    lines = text.split("\n")
    html_lines = []
    in_code = False
    in_list = False
    in_table = False
    table_rows = []

    for line in lines:
        # Code blocks
        if line.strip().startswith("```"):
            if in_code:
                html_lines.append("</code></pre>")
                in_code = False
            else:
                lang = line.strip()[3:]
                html_lines.append(f'<pre><code class="language-{html.escape(lang)}">')
                in_code = True
            continue

        if in_code:
            html_lines.append(html.escape(line))
            continue

        # Tables
        if "|" in line and line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(set(c) <= set("- :") for c in cells):
                continue  # separator row
            if not in_table:
                in_table = True
                table_rows = []
            table_rows.append(cells)
            continue
        elif in_table:
            html_lines.append(_render_table(table_rows))
            in_table = False
            table_rows = []

        # Lists
        if re.match(r"^[-*]\s", line.strip()):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            content = re.sub(r"^[-*]\s+", "", line.strip())
            html_lines.append(f"<li>{_inline(content)}</li>")
            continue
        elif in_list:
            html_lines.append("</ul>")
            in_list = False

        # Headings
        m = re.match(r"^(#{1,6})\s+(.+)", line)
        if m:
            level = len(m.group(1))
            html_lines.append(f"<h{level}>{_inline(m.group(2))}</h{level}>")
            continue

        # Empty line
        if not line.strip():
            html_lines.append("")
            continue

        # Regular paragraph
        html_lines.append(f"<p>{_inline(line)}</p>")

    if in_list:
        html_lines.append("</ul>")
    if in_table:
        html_lines.append(_render_table(table_rows))

    return "\n".join(html_lines)


def _inline(text: str) -> str:
    """Convert inline markdown (bold, italic, code, links)."""
    text = html.escape(text)
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # Inline code
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    # Links
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)
    return text


def _render_table(rows: list[list[str]]) -> str:
    """Render a table from rows."""
    if not rows:
        return ""
    lines = ["<table>"]
    # First row is header
    lines.append("<tr>" + "".join(f"<th>{_inline(c)}</th>" for c in rows[0]) + "</tr>")
    for row in rows[1:]:
        lines.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in row) + "</tr>")
    lines.append("</table>")
    return "\n".join(lines)


CSS = """body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 800px; margin: 2em auto; padding: 0 1em; color: #1f2937; line-height: 1.6; }
h1 { border-bottom: 2px solid #e5e7eb; padding-bottom: 0.3em; }
h2 { margin-top: 1.5em; }
h3 { margin-top: 1.2em; }
code { background: #f3f4f6; padding: 2px 4px; border-radius: 3px; font-size: 0.9em; }
pre { background: #f3f4f6; padding: 1em; border-radius: 8px; overflow-x: auto; }
pre code { background: none; padding: 0; }
table { width: 100%; border-collapse: collapse; margin: 1em 0; }
th, td { text-align: left; padding: 8px; border-bottom: 1px solid #e5e7eb; }
th { background: #f3f4f6; }
a { color: #2563eb; }
nav { margin-bottom: 2em; padding: 1em; background: #f9fafb; border-radius: 8px; }
nav a { margin-right: 1em; }"""


def build_site(docs_dir: str, output_dir: str) -> None:
    """Build the docs site."""
    docs = Path(docs_dir)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Write CSS
    (out / "style.css").write_text(CSS, encoding="utf-8")

    # Convert each markdown file
    count = 0
    for md_file in sorted(docs.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        title = md_file.stem.replace("-", " ").title()
        body = _md_to_html(content)

        page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} — oss-paper-ci</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<nav><a href="index.html">Index</a> | <a href="getting-started.html">Getting Started</a> | <a href="cli-reference.html">CLI Reference</a> | <a href="demo-gallery.html">Gallery</a></nav>
{body}
</body>
</html>"""

        (out / f"{md_file.stem}.html").write_text(page, encoding="utf-8")
        count += 1

    print(f"Built {count} pages to {output_dir}/")


def main():
    parser = argparse.ArgumentParser(description="Build docs site")
    parser.add_argument("--docs", default="docs", help="Docs source directory")
    parser.add_argument("--output", default="site", help="Output directory")
    args = parser.parse_args()

    build_site(args.docs, args.output)


if __name__ == "__main__":
    main()
