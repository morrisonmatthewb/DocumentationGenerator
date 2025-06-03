"""
PDF generation utilities with fallback options.
"""

from io import BytesIO
import markdown2
import streamlit as st


def convert_markdown_to_html(markdown_content: str, title: str = "Documentation") -> str:
    """
    Convert markdown content to HTML.
    
    Args:
        markdown_content: String containing markdown content
        title: Title of the document
    
    Returns:
        HTML content as string
    """
    # Convert Markdown to HTML with extra features
    html_content = markdown2.markdown(
        markdown_content,
        extras=[
            "fenced-code-blocks", 
            "tables", 
            "header-ids", 
            "toc",
            "code-friendly",
            "cuddled-lists",
            "footnotes"
        ]
    )
    
    # Define CSS
    css = """
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            padding: 20px;
            max-width: 800px;
            margin: 0 auto;
        }
        h1 {
            color: #1E3A8A;
            border-bottom: 1px solid #ddd;
            padding-bottom: 0.3em;
        }
        h2 {
            color: #2563EB;
            margin-top: 1.5em;
        }
        h3 {
            color: #3B82F6;
        }
        pre {
            background-color: #f6f8fa;
            border-radius: 6px;
            padding: 16px;
            overflow: auto;
        }
        code {
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            background-color: rgba(175, 184, 193, 0.2);
            padding: 0.2em 0.4em;
            border-radius: 6px;
            font-size: 85%;
        }
        pre code {
            background-color: transparent;
            padding: 0;
        }
        blockquote {
            border-left: 4px solid #ddd;
            padding-left: 16px;
            color: #57606a;
            margin-left: 0;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 16px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px 16px;
            text-align: left;
        }
        th {
            background-color: #f6f8fa;
        }
        @media print {
            body { font-size: 12pt; }
            pre, code { font-size: 10pt; }
        }
    """
    
    # Wrap with HTML structure
    html_document = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
        <style>
        {css}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        {html_content}
    </body>
    </html>
    """
    
    return html_document
