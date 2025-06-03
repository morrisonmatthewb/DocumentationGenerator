# Setup Guide - Documentation Generator

This guide will walk you through setting up the Documentation Generator on your system.

## Prerequisites

### System Requirements

* **Python 3.8 or higher** (Python 3.9+ recommended)
* **4GB+ RAM** (8GB+ recommended for large projects)
* **Internet connection** (for Claude API access)
* **Web browser** (Chrome, Firefox, Safari, or Edge)

### Required Accounts

* **Anthropic API Key** - Sign up at [console.anthropic.com](https://console.anthropic.com/)

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd advanced-documentation-generator
```

### 2. Install Python Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

### 3. Set Up API Key

```bash
# Copy the environment template
cp .env.example .env

# Edit the .env file with your API key
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
```

### 4. Run the Application

```bash
streamlit run app_concurrent.py
```

The app will open in your browser at `http://localhost:8501`

## Detailed Installation

### Step 1: Python Environment Setup

#### Option A: Using pip (Recommended)

```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Option B: Using conda

```bash
# Create conda environment
conda create -n docgen python=3.9
conda activate docgen

# Install dependencies
pip install -r requirements.txt
```

#### Option C: Using Poetry

```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install
poetry shell
```

### Step 2: Archive Support

For full archive format support, install additional dependencies:

```bash
# For 7z support
pip install py7zr

# For RAR support
pip install rarfile

# For additional archive formats
pip install patoolib
```

 **Note** : Some archive formats may require system-level tools:

* **RAR** : Install WinRAR or unrar
* **7z** : Install 7-Zip
* **TAR/GZ/BZ2** : Usually included with Python

### Step 3: API Key Configuration

#### Method 1: Environment File (Recommended)

```bash
# Create .env file
cp .env.example .env

# Edit with your favorite editor
nano .env
# or
code .env
```

Add your API key:

```bash
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### Method 2: System Environment Variable

```bash
# On Windows (Command Prompt)
set ANTHROPIC_API_KEY=your_api_key_here

# On Windows (PowerShell)
$env:ANTHROPIC_API_KEY="your_api_key_here"

# On macOS/Linux
export ANTHROPIC_API_KEY=your_api_key_here
```

#### Method 3: Streamlit Secrets

```bash
# Create Streamlit secrets directory
mkdir -p ~/.streamlit

# Add to secrets.toml
echo 'ANTHROPIC_API_KEY = "your_api_key_here"' >> ~/.streamlit/secrets.toml
```

### Step 4: Configuration (Optional)

#### Customize Application Settings

Edit `config/constants.py` to customize:

```python
# Documentation detail levels
DEFAULT_DOC_LEVEL = "comprehensive"  # basic, comprehensive, expert

# File size limits (MB)
DEFAULT_MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_RANGE = (1, 20)

# Claude API settings
DEFAULT_MODEL = "claude-3-7-sonnet-20250219"
DEFAULT_TEMPERATURE = 0.2
```

#### Add Custom File Types

```python
# In config/constants.py
SUPPORTED_EXTENSIONS = {
    # Add your custom file types
    '.your_ext': 'Your Language',
    # ... existing types
}
```

#### Customize UI Theme

```python
# In config/constants.py, modify APP_CSS
APP_CSS = """
    h1, h2, h3 {
        color: #your_color;  # Change heading color
    }
    .stButton>button {
        background-color: #your_color;  # Change button color
    }
"""
```

## Testing Your Installation

### 1. Basic Functionality Test

```bash
# Run the application
streamlit run app_concurrent.py

# Check that it loads without errors
# Try uploading a small test archive
```

### 2. API Connection Test

```python
# Test your API key in Python
import anthropic
client = anthropic.Anthropic(api_key="your_api_key")
response = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=100,
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.content[0].text)
```

### 3. Archive Support Test

Create a test ZIP file with some code files and try uploading it through the interface.

## Troubleshooting

### Common Issues

#### 1. **API Key Issues**

```
Error: Failed to initialize Claude client
```

**Solutions:**

* Verify your API key is correct
* Check that you have credits in your Anthropic account
* Ensure the API key has proper permissions

#### 2. **Import Errors**

```
ModuleNotFoundError: No module named 'streamlit'
```

**Solutions:**

* Ensure virtual environment is activated
* Re-run `pip install -r requirements.txt`
* Check Python version compatibility

#### 3. **Archive Extraction Errors**

```
Error extracting archive: Failed to extract archive
```

**Solutions:**

* Install additional archive support: `pip install py7zr rarfile patoolib`
* Check that the uploaded file is a valid archive
* Ensure the archive isn't corrupted

#### 4. **Memory Issues**

```
MemoryError or app crashes with large files
```

**Solutions:**

* Reduce max file size in settings
* Use fewer concurrent workers
* Switch to Sequential processing mode
* Close other applications to free up RAM

#### 5. **Port Already in Use**

```
Address already in use
```

**Solutions:**

```bash
# Use a different port
streamlit run app_concurrent.py --server.port 8502

# Or kill existing Streamlit processes
pkill -f streamlit
```

#### 6. **Browser Not Opening**

```bash
# Manually open browser
streamlit run app_concurrent.py --server.headless true
# Then visit http://localhost:8501
```

### Debug Mode

Enable debug logging:

```bash
# Run with debug output
streamlit run app_concurrent.py --logger.level debug

# Or set environment variable
export STREAMLIT_LOGGER_LEVEL=debug
streamlit run app_concurrent.py
```

### Performance Tuning

#### For Large Projects

```python
# In config/constants.py
DEFAULT_MAX_FILE_SIZE_MB = 10  # Increase if needed
MAX_FILE_SIZE_RANGE = (1, 50)  # Allow larger files

# Use fewer concurrent workers to avoid API limits
# Set in sidebar: Max Workers = 2-3
```

#### For Slow Connections

```python
# Increase timeouts in utils/api.py
# Add timeout parameters to API calls
response = client.messages.create(
    # ... other parameters
    timeout=60.0  # Increase timeout
)
```

### Security Considerations

#### API Key Security

* ✅ Use `.env` files (never commit API keys)
* ✅ Set proper file permissions: `chmod 600 .env`
* ✅ Use environment variables in production
* ❌ Never hardcode API keys in source code

#### File Upload Security

* The app processes uploaded archives - only upload trusted files
* Archives are extracted to temporary directories and cleaned up
* File size limits help prevent resource exhaustion

## Dependencies

### Required Packages

```
streamlit>=1.28.0          # Web application framework
anthropic>=0.3.0           # Claude AI API client
python-dotenv>=0.19.0      # Environment variable management
markdown2>=2.4.0           # Markdown to HTML conversion
```

### Optional Packages

```
py7zr>=0.20.0             # 7z archive support
rarfile>=4.0              # RAR archive support  
patoolib>=1.12.0          # Additional archive formats
```

### Archive Format Support Matrix

| Format     | Required Package | Notes                      |
| ---------- | ---------------- | -------------------------- |
| ZIP        | ✅ Built-in      | Python standard library    |
| TAR/GZ/BZ2 | ✅ Built-in      | Python standard library    |
| 7Z         | `py7zr`        | Install with pip           |
| RAR        | `rarfile`      | May need system unrar tool |
| Others     | `patoolib`     | Requires system tools      |
