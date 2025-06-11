# Documentation Generator

Documentation generator that uses Claude AI to automatically create comprehensive documentation for your code projects.

## Features

### **Core Capabilities**

* **AI-Powered Documentation** - Uses Claude AI to generate documentation
* **Multi-Language Support** - Supports 47+ programming languages and file types
* **Concurrent Processing** - Fast documentation generation with batch and concurrent processing modes
* **Archive Support** - Handles ZIP, 7z, RAR, TAR, and other common archive formats
* **Multiple Export Formats** - Download as Markdown, JSON, or interactive HTML

### **Smart Analysis**

* **Project Overview** - Automatically generates high-level project summaries
* **Directory Structure** - Visual directory trees with ASCII and interactive Mermaid diagrams
* **File Categorization** - Organizes files by language and purpose
* **Dependency Analysis** - Identifies and documents project dependencies
* **Suggested Improvements** - Provides suggestions to improve project based on industry standard SE principles.

### **User Experience**

* **Session History** - Keep track of previously generated documentation
* **Categorized File Selection** - Organized file type selection by category
* **Responsive Design** - Clean, modern interface that works on all devices

### **Performance**

* **Three Processing Modes** :
* **Sequential** - One file at a time (for debugging)
* **Batch Processing** - Process files in small batches (recommended)
* **Full Concurrent** - Maximum parallelization (for large projects, not recommended)
* **Smart Memory Management** - Configurable file size limits and efficient processing

## Supported Languages & Technologies

### Programming Languages

Python • JavaScript • TypeScript • Java • C++ • C • C# • Go • Ruby • PHP • Swift • Rust • Kotlin • Dart • Scala • Haskell • Clojure

### Web & Frontend

HTML • CSS • SCSS • Sass • React JSX • React TSX • Vue.js • XML

### Database & Queries

SQL • PostgreSQL • PL/SQL

### Scripts & Shell

Shell • Bash • PowerShell • Batch • Lua • Perl

### Configuration & Data

YAML • JSON • TOML • INI • Environment • Properties

### Documentation

Markdown • reStructuredText • LaTeX

### Build & Deployment

Dockerfile • Makefile • Gradle

### Data Science

R • Julia • MATLAB

### Headers & Interfaces

C/C++ Headers • Python Interface Files

## Installation

See [SETUP.md](https://claude.ai/chat/SETUP.md) for detailed installation instructions.

**Quick Start:**

```bash
# Clone the repository
git clone <your-repo-url>
cd advanced-documentation-generator

# Install dependencies
pip install -r requirements.txt

# Set up your API key
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env

# Run the application
streamlit run app_concurrent.py
```

## Usage

### Basic Workflow

1. **Start the Application**
   ```bash
   streamlit run app_concurrent.py
   ```
2. **Configure Settings**
   * Enter your Anthropic API key (or set it in `.env`)
   * Choose documentation detail level (basic/comprehensive/expert)
   * Select file types to process
   * Choose processing method
3. **Upload Project**
   * Upload a ZIP, 7z, RAR, or TAR archive of your project
   * Review the extracted files summary
4. **Generate Documentation**
   * Click "Generate Documentation"
   * Monitor progress in real-time
   * Review generated documentation
5. **Download & Share**
   * Download as Markdown, JSON, or HTML
   * Access previous generations from history tab

### Processing Modes

| Mode                       | Best For                       | Speed   | Stability   |
| -------------------------- | ------------------------------ | ------- | ----------- |
| **Sequential**       | Small projects, debugging      | Slowest | Most stable |
| **Batch Processing** | Most projects (recommended)    | Fast    | Very stable |
| **Full Concurrent**  | Large projects, speed critical | Fastest | Good        |

### Documentation Levels

* **Basic** - Essential information only (faster generation)
* **Comprehensive** - Balanced detail level (recommended)
* **Expert** - Extremely detailed with advanced insights

## Project Structure

```
advanced-documentation-generator/
├── core/                          # Core documentation generation logic
│   ├── __init__.py
│   ├── docgen.py                 # Sequential documentation generation
│   └── concurrent_docgen.py      # Concurrent/batch processing
├── utils/                         # Utility functions
│   ├── __init__.py
│   ├── api.py                    # Claude API integration
│   ├── archive.py                # Archive extraction
│   ├── documentation.py          # Documentation processing
│   ├── documentation_history.py  # Session history management
│   ├── html.py                   # HTML generation
│   ├── ui.py                     # User interface components
│   └── visualization.py          # Directory tree generation
├── config/                        # Configuration settings
│   ├── __init__.py
│   └── constants.py              # App constants and file types
├── app_concurrent.py             # Main application
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
├── README.md                     # This file
└── SETUP.md                      # Detailed setup instructions
```

## 🔧 Configuration

### Environment Variables

```bash
# Optional personal api key to default to
ANTHROPIC_API_KEY=str

# Variables for demo mode
DEMO_KEY=str
DEMO_PW=str

# Enables some debug elements
DEBUG=bool
```

### Customization

* **File Types** : Edit `SUPPORTED_EXTENSIONS` in `config/constants.py`
* **UI Theme** : Modify `APP_CSS` in `config/constants.py`
* **API Settings** : Adjust `DEFAULT_MODEL` and `DEFAULT_TEMPERATURE` and max token settings

## Performance Tips

1. **Choose the Right Processing Mode**

   * Use Batch Processing for most projects
   * Only use Full Concurrent for very large projects
   * Use Sequential only for debugging
2. **Optimize File Selection**

   * Deselect file types you don't need
   * Adjust max file size to skip large files
   * Focus on core source files
3. **API Considerations**

   * Claude has rate limits - Batch Processing helps avoid them
   * Comprehensive level provides best value/speed ratio
   * Expert level is slower but provides more detail

## License

This project is licensed under the MIT License - see the [LICENSE](https://claude.ai/chat/LICENSE) file for details.
