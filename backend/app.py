# app.py
"""
MarkdownBook PDF Studio - Backend API
Professional Markdown to PDF converter with FastAPI and WeasyPrint
"""

import os
import re
import base64
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
import markdown_it
from mdit_py_plugins import footnote, tasklists
import pygments
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration
import requests
from PIL import Image
import io

# Initialize FastAPI app
app = FastAPI(
    title="MarkdownBook PDF Studio",
    description="Professional Markdown to PDF converter",
    version="1.0.0"
)

# Font configuration for WeasyPrint
font_config = FontConfiguration()

# CSS for PDF styling
PDF_CSS = '''
/* PDF Professional Styles */
@page {
    size: A4;
    margin: 1in;
    
    @top-center {
        content: string(document-title);
        font-family: 'Liberation Sans', 'DejaVu Sans', sans-serif;
        font-size: 9pt;
        color: #666;
        border-bottom: 0.5px solid #ddd;
        padding-bottom: 5px;
    }
    
    @bottom-center {
        content: counter(page) " / " counter(pages);
        font-family: 'Liberation Sans', 'DejaVu Sans', sans-serif;
        font-size: 9pt;
        color: #666;
        border-top: 0.5px solid #ddd;
        padding-top: 5px;
    }
}

@page:first {
    @top-center {
        content: none;
    }
    
    @bottom-center {
        content: none;
    }
}

:root {
    --primary-color: #2563eb;
    --text-color: #1a1a1a;
    --bg-color: #ffffff;
    --border-color: #e5e7eb;
    --callout-note-bg: #eff6ff;
    --callout-note-border: #3b82f6;
    --callout-tip-bg: #f0fdf4;
    --callout-tip-border: #22c55e;
    --callout-warning-bg: #fef2f2;
    --callout-warning-border: #ef4444;
    --table-header-bg: #f8fafc;
    --table-border: #e2e8f0;
    --table-stripe: #f8fafc;
}

body {
    font-family: 'DejaVu Serif', 'Liberation Serif', 'Times New Roman', serif;
    font-size: 12pt;
    line-height: 1.8;
    color: var(--text-color);
    margin: 0;
    padding: 0;
}

/* Cover Page */
.cover-page {
    page-break-after: always;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 80vh;
    text-align: center;
    padding: 2in 1in;
}

.cover-page .cover-title {
    font-family: 'Liberation Sans Bold', 'DejaVu Sans', sans-serif;
    font-size: 42pt;
    font-weight: 700;
    color: var(--primary-color);
    margin-bottom: 20pt;
    line-height: 1.2;
}

.cover-page .cover-subtitle {
    font-family: 'Liberation Sans', 'DejaVu Sans', sans-serif;
    font-size: 18pt;
    color: #64748b;
    margin-bottom: 40pt;
    font-weight: 300;
}

.cover-page .cover-divider {
    width: 100pt;
    height: 2pt;
    background: var(--primary-color);
    margin-bottom: 40pt;
}

.cover-page .cover-author {
    font-family: 'Liberation Sans', 'DejaVu Sans', sans-serif;
    font-size: 14pt;
    color: #475569;
    margin-bottom: 20pt;
}

.cover-page .cover-date {
    font-family: 'Liberation Sans', 'DejaVu Sans', sans-serif;
    font-size: 12pt;
    color: #94a3b8;
}

/* Table of Contents */
.toc {
    page-break-after: always;
    padding: 20px 0;
}

.toc h2 {
    font-family: 'Liberation Sans Bold', 'DejaVu Sans', sans-serif;
    font-size: 24pt;
    color: var(--primary-color);
    border-bottom: 3px solid var(--primary-color);
    padding-bottom: 10px;
    margin-bottom: 30px;
}

.toc-entry {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 8px;
    padding: 4px 0;
    border-bottom: 1px dotted #ccc;
}

.toc-entry a {
    text-decoration: none;
    color: var(--text-color);
    font-family: 'DejaVu Serif', serif;
    font-size: 11pt;
}

.toc-entry .toc-page {
    color: #666;
    font-size: 10pt;
}

.toc-entry.toc-level-1 { margin-left: 0; }
.toc-entry.toc-level-2 { margin-left: 20px; }
.toc-entry.toc-level-3 { margin-left: 40px; }

/* Headings */
h1 {
    font-family: 'Liberation Sans Bold', 'DejaVu Sans', sans-serif;
    font-size: 34px;
    font-weight: 700;
    color: var(--text-color);
    margin-top: 40px;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 3px solid var(--primary-color);
    page-break-after: avoid;
}

h2 {
    font-family: 'Liberation Sans Bold', 'DejaVu Sans', sans-serif;
    font-size: 28px;
    font-weight: 600;
    color: var(--text-color);
    margin-top: 35px;
    margin-bottom: 18px;
    padding-left: 15px;
    border-left: 5px solid var(--primary-color);
    page-break-after: avoid;
}

h3 {
    font-family: 'Liberation Sans', 'DejaVu Sans', sans-serif;
    font-size: 22px;
    font-weight: 600;
    color: var(--text-color);
    margin-top: 30px;
    margin-bottom: 15px;
    padding: 8px 15px;
    background-color: #f0f4ff;
    border-radius: 4px;
    page-break-after: avoid;
}

h4 {
    font-family: 'Liberation Sans', 'DejaVu Sans', sans-serif;
    font-size: 18px;
    font-weight: 600;
    color: #444;
    margin-top: 25px;
    margin-bottom: 12px;
    page-break-after: avoid;
}

/* Paragraphs */
p {
    margin-bottom: 12px;
    text-align: justify;
    orphans: 3;
    widows: 3;
}

/* Lists */
ul, ol {
    line-height: 1.7;
    margin-bottom: 15px;
    padding-left: 30px;
}

li {
    margin-bottom: 5px;
}

/* Blockquotes */
blockquote {
    margin: 20px 0;
    padding: 15px 20px;
    border-left: 4px solid var(--primary-color);
    background: #f8fafc;
    font-style: italic;
    color: #475569;
    border-radius: 4px;
    page-break-inside: avoid;
}

blockquote p {
    margin: 0;
}

/* Callouts */
.callout {
    margin: 20px 0;
    padding: 15px 20px;
    border-radius: 8px;
    border-left: 5px solid;
    page-break-inside: avoid;
}

.callout-title {
    font-weight: 700;
    margin-bottom: 8px;
    font-family: 'Liberation Sans', 'DejaVu Sans', sans-serif;
}

.callout-note {
    background: var(--callout-note-bg);
    border-left-color: var(--callout-note-border);
}

.callout-tip {
    background: var(--callout-tip-bg);
    border-left-color: var(--callout-tip-border);
}

.callout-warning {
    background: var(--callout-warning-bg);
    border-left-color: var(--callout-warning-border);
}

/* Tables */
table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin: 20px 0;
    font-size: 10pt;
    line-height: 1.5;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    page-break-inside: avoid;
}

thead {
    display: table-header-group;
}

thead th {
    background: var(--table-header-bg);
    font-weight: 600;
    padding: 12px 15px;
    border-bottom: 2px solid var(--table-border);
    text-align: left;
    font-family: 'Liberation Sans', 'DejaVu Sans', sans-serif;
}

tbody td {
    padding: 10px 15px;
    border-bottom: 1px solid var(--table-border);
}

tbody tr:nth-child(even) {
    background: var(--table-stripe);
}

tbody tr:last-child td {
    border-bottom: none;
}

/* Code Blocks */
pre {
    background: #1e293b;
    color: #e2e8f0;
    padding: 20px;
    border-radius: 8px;
    overflow-x: auto;
    font-family: 'DejaVu Sans Mono', 'Liberation Mono', 'Courier New', monospace;
    font-size: 9pt;
    line-height: 1.6;
    margin: 20px 0;
    page-break-inside: avoid;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    position: relative;
}

code {
    font-family: 'DejaVu Sans Mono', 'Liberation Mono', 'Courier New', monospace;
    background: #f1f5f9;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 10pt;
}

pre code {
    background: transparent;
    padding: 0;
    font-size: 9pt;
}

.code-language-label {
    position: absolute;
    top: 5px;
    right: 15px;
    font-size: 8pt;
    color: #94a3b8;
    font-family: 'Liberation Sans', sans-serif;
    text-transform: uppercase;
    background: rgba(255,255,255,0.1);
    padding: 2px 8px;
    border-radius: 3px;
}

/* Images */
img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 20px auto;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.figure-caption {
    text-align: center;
    font-size: 10pt;
    color: #666;
    margin-top: 8px;
    margin-bottom: 20px;
    font-style: italic;
}

/* Links */
a {
    color: var(--primary-color);
    text-decoration: underline;
    text-underline-offset: 3px;
}

/* Horizontal Rules */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(to right, #e5e7eb, #94a3b8, #e5e7eb);
    margin: 30px 0;
}

/* Equations */
.equation-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 20px;
    margin: 20px 0;
    text-align: center;
    page-break-inside: avoid;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.equation-card .katex-display {
    margin: 0 !important;
}

/* Footnotes */
.footnote {
    font-size: 9pt;
    color: #666;
    margin-top: 20px;
    border-top: 1px solid #e5e7eb;
    padding-top: 10px;
}

/* Print optimizations */
@media print {
    body {
        print-color-adjust: exact;
        -webkit-print-color-adjust: exact;
    }
    
    h1, h2, h3, h4 {
        page-break-after: avoid;
    }
    
    table, pre, .equation-card {
        page-break-inside: avoid;
    }
}

strong {
    font-weight: 700;
    color: #1a1a1a;
}

em {
    font-style: italic;
}

del {
    text-decoration: line-through;
    color: #94a3b8;
}

u {
    text-decoration: underline;
}
'''

SYNTAX_CSS = '''
/* Pygments Syntax Highlighting */
.highlight .hll { background-color: #49483e }
.highlight { background: #1e293b; color: #e2e8f0; }
.highlight .c { color: #6c7a89 }
.highlight .k { color: #c678dd }
.highlight .l { color: #d19a66 }
.highlight .n { color: #e2e8f0 }
.highlight .o { color: #56b6c2 }
.highlight .p { color: #e2e8f0 }
.highlight .s { color: #98c379 }
.highlight .m { color: #d19a66 }
.highlight .nf { color: #61afef }
.highlight .nc { color: #e5c07b }
.highlight .kt { color: #e5c07b }
.highlight .kd { color: #c678dd }
.highlight .nb { color: #e2e8f0 }
.highlight .bp { color: #e2e8f0 }
'''

class MarkdownRequest(BaseModel):
    markdown: str

class MarkdownParser:
    """Custom Markdown to HTML parser"""
    
    def __init__(self):
        self.md = markdown_it.MarkdownIt(
            'commonmark',
            {
                'html': True,
                'typographer': True,
                'linkify': True,
                'breaks': True,
            }
        )
        
        # Add plugins
        self.md.use(footnote.footnote_plugin)
        self.md.use(tasklists.tasklist_plugin)
        
        # Enable extensions
        self.md.enable(['table', 'strikethrough'])
        
        self.figure_counter = 0
        self.table_counter = 0
        self.headings_list = []
        
    def parse(self, text: str) -> str:
        """Parse markdown to HTML"""
        
        # Pre-process callouts
        text = self._process_callouts(text)
        
        # Pre-process equations
        text = self._process_equations(text)
        
        # Parse markdown
        html = self.md.render(text)
        
        # Post-process HTML
        html = self._post_process(html)
        
        # Generate TOC
        toc_html = self._generate_toc()
        
        if toc_html:
            html = toc_html + '\n<div class="content-start">' + html + '</div>'
        
        return html
    
    def _process_callouts(self, text: str) -> str:
        """Convert GitHub-style callouts"""
        
        def replace_callout(match):
            callout_type = match.group(1).upper()
            content = match.group(2)
            
            css_class = {
                'NOTE': 'callout-note',
                'TIP': 'callout-tip',
                'WARNING': 'callout-warning',
                'IMPORTANT': 'callout-warning',
                'CAUTION': 'callout-warning',
            }.get(callout_type, 'callout-note')
            
            icon = {
                'NOTE': '📝',
                'TIP': '💡',
                'WARNING': '⚠️',
                'IMPORTANT': '❗',
                'CAUTION': '🚫',
            }.get(callout_type, '📝')
            
            return f'<div class="callout {css_class}"><div class="callout-title">{icon} {callout_type}</div>{content}</div>'
        
        pattern = r'> \[!(\w+)\]\n((?:>\s?.*\n?)*)'
        return re.sub(pattern, replace_callout, text, flags=re.MULTILINE)
    
    def _process_equations(self, text: str) -> str:
        """Process LaTeX equations for KaTeX rendering"""
        
        def replace_display_math(match):
            equation = match.group(1).strip()
            return f'<div class="equation-card"><div class="katex-display">$${equation}$$</div></div>'
        
        def replace_inline_math(match):
            equation = match.group(1).strip()
            return f'<span class="katex-inline">${equation}$</span>'
        
        # Replace \[ ... \] display math (LaTeX style)
        text = re.sub(r'\\\[\s*(.+?)\s*\\\]', replace_display_math, text, flags=re.DOTALL)
        
        # Replace $$ ... $$ display math
        text = re.sub(r'\$\$\s*(.+?)\s*\$\$', replace_display_math, text, flags=re.DOTALL)
        
        # Replace inline math $ ... $
        text = re.sub(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)', replace_inline_math, text)
        
        return text
    
    def _post_process(self, html: str) -> str:
        """Post-process HTML"""
        
        self.figure_counter = 0
        self.table_counter = 0
        
        # Add language labels to code blocks
        def add_language_label(match):
            lang = match.group(1) or 'text'
            code = match.group(2)
            
            try:
                lexer = get_lexer_by_name(lang, stripall=True)
            except ClassNotFound:
                lexer = guess_lexer(code)
            
            formatter = HtmlFormatter(
                style='monokai',
                cssclass='highlight',
                linenos=False,
            )
            
            highlighted = pygments.highlight(code, lexer, formatter)
            
            return f'<div style="position: relative;">{highlighted}<div class="code-language-label">{lang}</div></div>'
        
        html = re.sub(
            r'<pre><code class="language-(\w+)">(.+?)</code></pre>',
            add_language_label,
            html,
            flags=re.DOTALL
        )
        
        # Process tables
        def enhance_table(match):
            self.table_counter += 1
            table_content = match.group(1)
            caption = f'<div class="figure-caption">Table {self.table_counter}</div>'
            return f'<div>{table_content}{caption}</div>'
        
        html = re.sub(r'<table>(.+?)</table>', enhance_table, html, flags=re.DOTALL)
        
        # Process images
        def enhance_image(match):
            self.figure_counter += 1
            img_tag = match.group(0)
            alt_match = re.search(r'alt="([^"]*)"', img_tag)
            alt_text = alt_match.group(1) if alt_match else f'Figure {self.figure_counter}'
            return f'<figure>{img_tag}<figcaption class="figure-caption">Figure {self.figure_counter}. {alt_text}</figcaption></figure>'
        
        html = re.sub(r'<img[^>]+>', enhance_image, html)
        
        # Collect headings for TOC
        self.headings_list = re.findall(r'<h([1-3]) id="([^"]*)">(.+?)</h\1>', html)
        
        return html
    
    def _generate_toc(self) -> str:
        """Generate table of contents"""
        if not self.headings_list:
            return ""
        
        toc_html = '<div class="toc"><h2>Table of Contents</h2>'
        
        for level, id_, text in self.headings_list:
            level_num = int(level)
            toc_html += f'<div class="toc-entry toc-level-{level_num}"><a href="#{id_}">{text}</a></div>'
        
        toc_html += '</div>'
        
        return toc_html
    
    def generate_cover(self, text: str) -> str:
        """Generate cover page"""
        
        title_match = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
        title = title_match.group(1) if title_match else "Document"
        
        subtitle_match = re.search(r'^##\s+(.+)$', text, re.MULTILINE)
        subtitle = subtitle_match.group(1) if subtitle_match else ""
        
        date_str = datetime.now().strftime("%B %d, %Y")
        
        cover_html = f'''
        <div class="cover-page">
            <div class="cover-title">{title}</div>
            {f'<div class="cover-subtitle">{subtitle}</div>' if subtitle else ''}
            <div class="cover-divider"></div>
            <div class="cover-date">{date_str}</div>
            <div class="cover-author">Generated by MarkdownBook PDF Studio</div>
        </div>
        '''
        
        return cover_html

def process_images_in_html(html: str) -> str:
    """Download and base64 encode remote images"""
    
    def process_img_src(match):
        src = match.group(1)
        
        if src.startswith('data:'):
            return match.group(0)
        
        try:
            parsed = urlparse(src)
            
            if parsed.scheme in ['http', 'https']:
                response = requests.get(src, timeout=10)
                img = Image.open(io.BytesIO(response.content))
                
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                max_width = 800
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85, optimize=True)
                img_base64 = base64.b64encode(buffer.getvalue()).decode()
                
                return match.group(0).replace(src, f'data:image/jpeg;base64,{img_base64}')
            
            elif Path(src).exists():
                with open(src, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode()
                
                ext = Path(src).suffix.lower()
                mime_types = {
                    '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                    '.png': 'image/png', '.gif': 'image/gif',
                    '.webp': 'image/webp',
                }
                mime = mime_types.get(ext, 'image/jpeg')
                
                return match.group(0).replace(src, f'data:{mime};base64,{img_data}')
                
        except Exception as e:
            print(f"Error processing image {src}: {e}")
            return match.group(0)
        
        return match.group(0)
    
    return re.sub(r'src="([^"]+)"', process_img_src, html)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main application page"""
    html_path = Path(__file__).parent / "index.html"
    
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return HTMLResponse(content=content)

@app.post("/generate-pdf")
async def generate_pdf(request: MarkdownRequest):
    """Generate professional PDF from markdown"""
    
    try:
        # Initialize parser
        parser = MarkdownParser()
        
        # Generate cover page
        cover_html = parser.generate_cover(request.markdown)
        
        # Parse markdown to HTML
        content_html = parser.parse(request.markdown)
        
        # Process images
        content_html = process_images_in_html(content_html)
        
        # Complete HTML document
        full_html = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MarkdownBook PDF</title>
            <style>
                {PDF_CSS}
                {SYNTAX_CSS}
            </style>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
            <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
        </head>
        <body>
            {cover_html}
            {content_html}
            <script>
                document.addEventListener("DOMContentLoaded", function() {{
                    renderMathInElement(document.body, {{
                        delimiters: [
                            {{left: "$$", right: "$$", display: true}},
                            {{left: "$", right: "$", display: false}},
                            {{left: "\\\\[", right: "\\\\]", display: true}}
                        ],
                        throwOnError: false
                    }});
                }});
            </script>
        </body>
        </html>
        '''
        
        # Generate PDF with WeasyPrint
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            HTML(string=full_html).write_pdf(
                tmp.name,
                font_config=font_config,
                presentational_hints=True,
                optimize_size=('fonts', 'images'),
            )
            
            with open(tmp.name, 'rb') as pdf_file:
                pdf_content = pdf_file.read()
            
            os.unlink(tmp.name)
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=document.pdf",
                "Content-Length": str(len(pdf_content)),
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
