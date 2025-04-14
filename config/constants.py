"""
Application constants and configuration settings.
"""

# Supported code file extensions
SUPPORTED_EXTENSIONS = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
    '.java': 'Java',
    '.cpp': 'C++',
    '.c': 'C',
    '.cs': 'C#',
    '.go': 'Go',
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.swift': 'Swift',
    '.rs': 'Rust',
    '.html': 'HTML',
    '.css': 'CSS',
    '.sql': 'SQL',
    '.sh': 'Shell',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.json': 'JSON',
    '.md': 'Markdown',
}

# Supported archive formats
SUPPORTED_ARCHIVE_FORMATS = {
    '.zip': 'ZIP',
    '.7z': '7-Zip',
    '.rar': 'RAR',
    '.tar': 'TAR',
    '.gz': 'GZIP',
    '.bz2': 'BZIP2',
    '.xz': 'XZ',
    '.tgz': 'TAR GZIP',
    '.tbz2': 'TAR BZIP2',
    '.tar.gz': 'TAR GZIP',
    '.tar.bz2': 'TAR BZIP2',
    '.tar.xz': 'TAR XZ',
}

# Claude API configuration
DEFAULT_MODEL = "claude-3-7-sonnet-20250219"
DEFAULT_TEMPERATURE = 0.2

# Documentation detail levels
DOC_LEVELS = ["basic", "comprehensive", "expert"]
DEFAULT_DOC_LEVEL = "comprehensive"

# File size limits
DEFAULT_MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_RANGE = (1, 20)

# Custom CSS for the application
APP_CSS = """
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        color: #1E3A8A;
    }
    .stButton>button {
        background-color: #1E3A8A;
        color: white;
    }
    .stProgress .st-bo {
        background-color: #1E3A8A;
    }
    /* Add styling for mermaid diagrams */
    .mermaid {
        text-align: center;
    }
"""

# Mermaid script for rendering diagrams
MERMAID_SCRIPT = """
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<script>
    mermaid.initialize({startOnLoad: true});
</script>
"""