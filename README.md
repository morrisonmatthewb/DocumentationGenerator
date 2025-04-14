
# Auto Documentation Generator

A web application that automatically generates documentation for code files in a zip archive using the Claude API.

## Features

- Upload archive files in multiple formats:
  - ZIP (.zip)
  - 7-Zip (.7z)
  - RAR (.rar)
  - TAR (.tar)
  - Compressed TAR (.tar.gz, .tar.bz2, .tar.xz, .tgz, .tbz2)
  - GZIP (.gz)
  - BZIP2 (.bz2)
  - XZ (.xz)
- Automatically extract and process code files
- Generate comprehensive documentation using Claude's AI
- Support for multiple programming languages:
  - Python
  - JavaScript
  - TypeScript
  - Java
  - C++
  - C
  - C#
  - Go
  - Ruby
  - PHP
  - Swift
  - Rust
  - HTML
  - CSS
  - SQL
  - Shell
  - YAML/YML
  - JSON
  - Markdown
- Configurable documentation detail levels
- Project overview generation
- Directory structure visualization with Mermaid diagrams
- Recursive directory support
- Download documentation as Markdown, JSON, or PDF
- File size limits to avoid processing very large files

## Installation

1. Clone this repository:

   ```
   git clone https://github.com/yourusername/auto-documentation-generator.git
   cd auto-documentation-generator
   ```
2. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```
3. For RAR file support, install additional dependencies:

   **On Ubuntu/Debian:**

   ```
   sudo apt-get install unrar
   ```

   **On macOS:**

   ```
   brew install unrar
   ```

   **On Windows:**
   Download and install WinRAR or UnRAR from https://www.rarlab.com/
4. For 7z and other archive formats, install external utilities:

   **On Ubuntu/Debian:**

   ```
   sudo apt-get install p7zip-full p7zip-rar
   ```

   **On macOS:**

   ```
   brew install p7zip
   ```

   **On Windows:**
   Download and install 7-Zip from https://www.7-zip.org/
5. For PDF export functionality, install WeasyPrint dependencies:

   **On Ubuntu/Debian:**

   ```
   apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
   ```

   **On macOS:**

   ```
   brew install cairo pango gdk-pixbuf libffi
   ```

   **On Windows:**
   See detailed instructions at: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows
6. Set up your Anthropic API key:

   - Create a `.env` file in the project root with:
     ```
     ANTHROPIC_API_KEY=your_api_key_here
     ```
   - Or, you can enter your API key in the web interface when prompted

## Usage

1. Start the web application:

   ```
   streamlit run app.py
   ```
2. Open your browser and navigate to the provided URL (typically http://localhost:8501)
3. Enter your Anthropic API key if prompted
4. Upload a zip file containing your code
5. Configure the documentation settings:

   - Select file types to process
   - Choose documentation detail level
   - Toggle project overview generation
6. Click "Generate Documentation"
7. View and download the generated documentation

## Example

For a project with the following structure:

```
project.zip
├── app.py
├── utils/
│   ├── helpers.py
│   └── config.py
├── static/
│   └── script.js
└── README.md
```

The tool will:

1. Extract and identify all code files
2. Generate documentation for each file
3. Create a project overview (if selected)
4. Provide downloadable documentation in your preferred format

## Requirements

- Python 3.7+
- Anthropic API key (Claude 3.7 Sonnet model)
- Internet connection

## License

MIT License
