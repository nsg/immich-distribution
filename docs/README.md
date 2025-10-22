# Immich Distribution Documentation (Zola)

This directory contains the Zola-based documentation site for Immich Distribution.

## Structure

- `site/` - The Zola site directory
  - `config.toml` - Site configuration
  - `content/` - Markdown content files
  - `templates/` - HTML templates
  - `static/` - Static assets (CSS, images)
  - `sass/` - Sass stylesheets
  
## Development

Run the development server:

```bash
make run
```

The site will be available at `http://<hostname>.lan.nsgsrv.net:1111`

## Building

Build the site:

```bash
make build
```

The built site will be in `site/build-out/`

## Adding Content

Content is organized in sections:

- `/about` - About page
- `/news` - Blog/news posts
- `/installation` - Installation guides
- `/configuration` - Configuration documentation
- `/guides` - How-to guides
- `/contribute` - Contribution information

To add a new page, create a `.md` file in the appropriate `content/` subdirectory with frontmatter:

```markdown
+++
title = "Page Title"
+++

# Page Title

Content here...
```

## Sidebar Navigation

Pages within sections (Configuration, Installation, Guides, etc.) automatically display a sidebar navigation showing:
- All pages in the current section
- Subsections with their pages

To disable the sidebar for a specific page, use the `page-no-sidebar.html` template:

```markdown
+++
title = "Page Title"
template = "page-no-sidebar.html"
+++
```
