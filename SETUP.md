# Documentation Generator Setup Guide

This guide explains how to set up and run the Documentation Generator application.

## Automatic Setup

We've provided an automated setup script that will install all necessary dependencies and run the application.

### On Linux/macOS:

1. Open a terminal in the project directory
2. Run the following command:
   ```bash
   ./run.sh
   ```
3. If prompted, enter your administrator password to install system dependencies
4. You'll be asked to enter your Anthropic API key if not already configured

### On Windows:

1. Open the project directory
2. Double-click on `run.bat`
3. If prompted with administrator requests, approve them to install dependencies
4. You'll be asked to enter your Anthropic API key if not already configured

## Setup Options

The setup script has several options:

* `--setup-only`: Only install dependencies without running the app
* `--venv PATH`: Specify a custom path for the virtual environment (default: `.venv`)

Example:

```bash
./run.sh --setup-only
```

## Manual Installation

If the automatic setup doesn't work for your system, you can follow these manual installation steps:

### System Dependencies

#### Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install -y python3-dev python3-pip python3-venv build-essential \
    libcairo2-dev libpango1.0-dev libgdk-pixbuf2.0-dev libffi-dev shared-mime-info \
    p7zip-full p7zip-rar unrar libxml2-dev libxslt1-dev
```

#### Fedora/RHEL/CentOS:

```bash
sudo dnf install -y python3-devel python3-pip gcc cairo-devel pango-devel \
    gdk-pixbuf2-devel libffi-devel redhat-rpm-config p7zip p7zip-plugins \
    unrar libxml2-devel libxslt-devel
```

#### macOS:

```bash
brew install cairo pango gdk-pixbuf libffi p7zip libxml2 libxslt unrar
```

#### Windows:

Install the following using chocolatey or manually:

- Python 3.7+
- 7zip
- unrar

### Python Setup

1. Create a virtual environment:

   ```bash
   python3 -m venv .venv
   ```
2. Activate the virtual environment:

   - On Linux/macOS: `source .venv/bin/activate`
   - On Windows: `.venv\Scripts\activate`
3. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your Anthropic API key:

   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```
5. Run the application:

   ```bash
   streamlit run app.py
   ```

## Troubleshooting

### PDF Generation Issues

If you encounter issues with PDF generation:

1. Ensure that you have installed all system dependencies for WeasyPrint
2. Try updating WeasyPrint: `pip install --upgrade weasyprint`
3. Fall back to the HTML export option, which should work automatically

### Archive Extraction Issues

If you have trouble extracting certain archive formats:

1. Ensure that the correct tools are installed (7zip, unrar)
2. Check if the archive requires a specific version of these tools
3. Try extracting the archive manually and then processing the extracted files

### Other Issues

If you encounter other issues:

1. Check the console output for specific error messages
2. Ensure that your Python version is 3.7 or higher
3. Try reinstalling the dependencies with `pip install --upgrade -r requirements.txt`
4. Check that your Anthropic API key is valid and correctly set in the `.env` file

For more detailed troubleshooting, please refer to the README.md file.
