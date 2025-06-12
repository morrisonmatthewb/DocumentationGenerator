import markdown2

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
    
    return enhance_html(html_document)

def enhance_html(html_content: str, title: str = "Project Documentation") -> str:
    """
    Enhance HTML with user experience features such as table of contents.
    
    Args:
        html_content: HTML content from convert_markdown_to_html
        title: Title for the document
        
    Returns:
        Enhanced HTML with navigation and interactive features
    """
    # Add navigation and interactive features to the existing HTML
    enhanced_features = """
        <!-- Navigation Panel -->
        <div id="navigation" class="navigation">
            <h3>📋 Contents</h3>
            <ul id="nav-list">
                <!-- Navigation will be populated by JavaScript -->
            </ul>
        </div>
        
        <style>
        /* Additional styles for viewer features */
        .navigation {
            position: fixed;
            top: 20px;
            left: 20px;
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            max-height: 80vh;
            overflow-y: auto;
            min-width: 200px;
            max-width: 300px;
            z-index: 1000;
        }
        
        .navigation h3 {
            margin: 0 0 12px 0;
            font-size: 16px;
            color: #374151;
            border-bottom: 1px solid #E5E7EB;
            padding-bottom: 8px;
        }
        
        .navigation ul {
            margin: 0;
            padding: 0;
            list-style: none;
        }
        
        .navigation li {
            margin: 6px 0;
        }
        
        .navigation a {
            font-size: 13px;
            padding: 6px 10px;
            display: block;
            border-radius: 4px;
            transition: all 0.2s ease;
            text-decoration: none;
            color: #4B5563;
        }
        
        .navigation a:hover {
            background-color: #F3F4F6;
            color: #1E3A8A;
            transform: translateX(2px);
        }
        
        .navigation .nav-level-1 { padding-left: 10px; font-weight: 600; }
        .navigation .nav-level-2 { padding-left: 20px; }
        .navigation .nav-level-3 { padding-left: 30px; font-size: 12px; }
        .navigation .nav-level-4 { padding-left: 40px; font-size: 12px; }
        
        pre {
            position: relative;
        }
        
        .copy-button {
            position: absolute;
            top: 8px;
            right: 8px;
            background: #374151;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
            opacity: 0;
            transition: opacity 0.2s ease;
        }
        
        pre:hover .copy-button {
            opacity: 1;
        }
        
        .copy-button:hover {
            background: #1F2937;
        }
        
        .copy-button.copied {
            background: #059669;
        }
        
        @media (max-width: 768px) {
            .navigation {
                position: relative;
                top: auto;
                right: auto;
                margin: 20px auto;
                max-width: 90%;
            }
            
            body {
                padding: 12px;
            }
        }
        
        @media print {
            .navigation {
                display: none;
            }
        }
        
        /* Smooth scrolling */
        html {
            scroll-behavior: smooth;
        }
        
        /* Highlight target section */
        :target {
            animation: highlight 2s ease-in-out;
        }
        
        @keyframes highlight {
            0% { background-color: #FEF3C7; }
            100% { background-color: transparent; }
        }
        </style>
        
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Generate navigation from headings
            function generateNavigation() {
                const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
                const navList = document.getElementById('nav-list');
                
                if (headings.length === 0) {
                    document.getElementById('navigation').style.display = 'none';
                    return;
                }
                
                headings.forEach((heading, index) => {
                    // Create ID if it doesn't exist
                    if (!heading.id) {
                        heading.id = 'heading-' + index;
                    }
                    
                    const level = parseInt(heading.tagName.charAt(1));
                    const li = document.createElement('li');
                    const a = document.createElement('a');
                    
                    a.href = '#' + heading.id;
                    a.textContent = heading.textContent;
                    a.className = 'nav-level-' + level;
                    
                    li.appendChild(a);
                    navList.appendChild(li);
                });
            }
            
            function addSearchFunctionality() {
                const nav = document.getElementById('navigation');
                const searchInput = document.createElement('input');
                searchInput.type = 'text';
                searchInput.placeholder = 'Search documentation...';
                searchInput.style.cssText = `
                    width: 100%;
                    padding: 8px;
                    margin-bottom: 12px;
                    border: 1px solid #D1D5DB;
                    border-radius: 4px;
                    font-size: 14px;
                `;
                
                nav.insertBefore(searchInput, nav.querySelector('h3').nextSibling);
                
                searchInput.addEventListener('input', function() {
                    const searchTerm = this.value.toLowerCase();
                    const content = document.body.textContent.toLowerCase();
                    
                    // Simple highlight search (you could make this more sophisticated)
                    if (searchTerm.length > 2) {
                        // This is a basic implementation - could be enhanced
                        console.log('Searching for:', searchTerm);
                    }
                });
            }
            
            // Initialize features
            generateNavigation();
            addSearchFunctionality();
            
        });
        </script>
    """
    
    # Insert the enhanced features before the closing body tag
    if "</body>" in html_content:
        html_content = html_content.replace("</body>", enhanced_features + "</body>")
    else:
        html_content += enhanced_features
    
    return html_content


