"""
Application constants and configuration settings.
"""

SUPPORTED_EXTENSIONS = {
    # Core programming languages
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".cs": "C#",
    ".go": "Go",
    ".rb": "Ruby",
    ".php": "PHP",
    ".swift": "Swift",
    ".rs": "Rust",
    # Web technologies
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sass": "Sass",
    ".jsx": "React JSX",
    ".tsx": "React TSX",
    ".vue": "Vue.js",
    ".xml": "XML",
    # Modern languages & frameworks
    ".kt": "Kotlin",
    ".dart": "Dart",
    ".scala": "Scala",
    ".hs": "Haskell",
    ".clj": "Clojure",
    # Database & queries
    ".sql": "SQL",
    ".psql": "PostgreSQL",
    ".plsql": "PL/SQL",
    # Scripts & shell
    ".sh": "Shell",
    ".bash": "Bash",
    ".ps1": "PowerShell",
    ".bat": "Batch",
    ".lua": "Lua",
    ".pl": "Perl",
    # Configuration & data
    ".yaml": "YAML",
    ".yml": "YAML",
    ".json": "JSON",
    ".toml": "TOML",
    ".ini": "INI Config",
    ".env": "Environment",
    ".properties": "Properties",
    # Documentation & markup
    ".md": "Markdown",
    ".rst": "reStructuredText",
    ".tex": "LaTeX",
    # Build & deployment
    ".dockerfile": "Dockerfile",
    ".makefile": "Makefile",
    ".gradle": "Gradle",
    # Data science
    ".r": "R",
    ".R": "R",
    ".jl": "Julia",
    ".m": "MATLAB",
    # Headers & interfaces
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".pyi": "Python Interface",
}

FILE_TYPE_CATEGORIES = {
    "Programming Languages": [
        (".py", "Python"),
        (".js", "JavaScript"),
        (".ts", "TypeScript"),
        (".java", "Java"),
        (".cpp", "C++"),
        (".c", "C"),
        (".cs", "C#"),
        (".go", "Go"),
        (".rb", "Ruby"),
        (".php", "PHP"),
        (".swift", "Swift"),
        (".rs", "Rust"),
        (".kt", "Kotlin"),
        (".dart", "Dart"),
        (".scala", "Scala"),
    ],
    "Web & Frontend": [
        (".html", "HTML"),
        (".css", "CSS"),
        (".scss", "SCSS"),
        (".sass", "Sass"),
        (".jsx", "React JSX"),
        (".tsx", "React TSX"),
        (".vue", "Vue.js"),
        (".xml", "XML"),
    ],
    "Database & Queries": [
        (".sql", "SQL"),
        (".psql", "PostgreSQL"),
        (".plsql", "PL/SQL"),
    ],
    "Scripts & Shell": [
        (".sh", "Shell"),
        (".bash", "Bash"),
        (".ps1", "PowerShell"),
        (".bat", "Batch"),
        (".lua", "Lua"),
        (".pl", "Perl"),
    ],
    "Configuration & Data": [
        (".yaml", "YAML"),
        (".yml", "YAML"),
        (".json", "JSON"),
        (".toml", "TOML"),
        (".ini", "INI Config"),
        (".env", "Environment"),
        (".properties", "Properties"),
    ],
    "Documentation": [
        (".md", "Markdown"),
        (".rst", "reStructuredText"),
        (".tex", "LaTeX"),
    ],
    "Other": [
        (".dockerfile", "Dockerfile"),
        (".makefile", "Makefile"),
        (".gradle", "Gradle"),
        (".r", "R"),
        (".R", "R"),
        (".jl", "Julia"),
        (".m", "MATLAB"),
        (".h", "C/C++ Header"),
        (".hpp", "C++ Header"),
        (".pyi", "Python Interface"),
        (".hs", "Haskell"),
        (".clj", "Clojure"),
    ],
}

# Supported archive formats
SUPPORTED_ARCHIVE_FORMATS = {
    ".zip": "ZIP",
    ".7z": "7-Zip",
}
# ZipBomb protections
MAX_EXTRACT_SIZE = 300 * 1024 * 1024  
MAX_FILES = 1000  
MAX_UPLOAD_SIZE = 200 * 1024 * 1024   

# Claude API configuration
DEFAULT_MODEL = "claude-3-7-sonnet-20250219"
DEFAULT_TEMPERATURE = 0.2
BASIC_LEVEL_MAX_TOKENS=4000
COMPREHENSIVE_LEVEL_MAX_TOKENS=5000
EXPERT_LEVEL_MAX_TOKENS=7000
PROJECT_OVERVIEW_MAX_TOKENS=5000

# Documentation detail levels
DOC_LEVELS = ["basic", "comprehensive", "expert"]
DEFAULT_DOC_LEVEL = "comprehensive"

# File size limits
DEFAULT_MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_RANGE = (1, 20)
MAX_FILE_SIZE_DEMO_MODE = 5

# Concurrency limits
MIN_BATCH_SIZE = 2
MAX_BATCH_SIZE = 5
MAX_BATCH_SIZE_DEMO_MODE = 3
MIN_FULL_CONCURRENCY_THREADS = 2
MAX_FULL_CONCURRENCY_THREADS = 8

# Custom CSS for the application
APP_CSS = """
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        color: #5980f0;
    }
    .stButton>button {
        background-color: #5980f0;
        color: white;
    }
    .stProgress .st-bo {
        background-color: #5980f0;
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
