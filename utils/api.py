"""
Claude API integration utilities.
"""

import os
import anthropic
import streamlit as st
from config.constants import DEFAULT_MODEL, DEFAULT_TEMPERATURE
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import re


# Load environment variables
load_dotenv()


def is_valid_anthropic_api_key(api_key: str) -> bool:
    """Validate Anthropic API key format."""
    pattern = r"^sk-ant-api03-[a-zA-Z0-9_-]{95}$"
    return bool(re.match(pattern, api_key))


def get_api_key() -> Optional[str]:
    """
    Get the API key from environment, Streamlit secrets, or session state.
    No UI interaction - for core logic use.

    Returns:
        API key string or None if not available
    """
    # Try environment variable first
    api_key = os.getenv("ANTHROPIC_API_KEY")

    # Check session state if environment variable is not available
    if not api_key and "anthropic_api_key" in st.session_state:
        api_key = st.session_state.anthropic_api_key

    return api_key


def initialize_client(api_key: str) -> anthropic.Anthropic:
    """
    Initialize the Anthropic client with the given API key.

    Args:
        api_key: Anthropic API key

    Returns:
        Initialized Anthropic client

    Raises:
        Exception: If client initialization fails
    """
    try:
        return anthropic.Anthropic(api_key=api_key)
    except Exception as e:
        raise Exception(f"Failed to initialize Claude client: {str(e)}")


def get_language_prompt(language: str) -> str:
    """Get a language-specific prompt enhancement."""
    language_specific = {
        "Python": """
        For Python files, also include:
        - Docstring format compliance (Google style, NumPy, etc.)
        - Type hints usage
        - Recommended improvements to code organization
        """,
        "JavaScript": """
        For JavaScript files, also include:
        - ES6+ feature usage
        - Module pattern analysis
        - Potential browser compatibility issues
        """,
        "TypeScript": """
        For TypeScript files, also include:
        - Type system usage analysis
        - Interface and type definitions overview
        - Compilation target considerations
        """,
        "Java": """
        For Java files, also include:
        - Class hierarchy analysis
        - Design patterns used
        - Exception handling overview
        """,
    }

    return language_specific.get(language, "")


def generate_documentation(
    file_path: str,
    file_info: Dict[str, Any],
    client: anthropic.Anthropic,
    doc_level: str = "comprehensive",
) -> str:
    """
    Generate documentation for a single file using Claude API.

    Args:
        file_path: Path of the file within the archive
        file_info: Dict containing file content and language
        client: Anthropic client instance
        doc_level: Level of detail for documentation ("basic", "comprehensive", "expert")

    Returns:
        Generated documentation text
    """
    content = file_info["content"]
    language = file_info["language"]

    # Determine detail level
    if doc_level == "basic":
        detail_instruction = "Provide a basic overview with essential information only."
        max_tokens = 2000
    elif doc_level == "expert":
        detail_instruction = "Provide extremely detailed documentation with advanced insights and best practices."
        max_tokens = 6000
    else:
        detail_instruction = (
            "Provide comprehensive documentation with a good balance of detail."
        )
        max_tokens = 4000

    # Get language-specific prompting
    language_specific = get_language_prompt(language)

    prompt = f"""
    Please generate {doc_level} documentation for the following {language} file.
    {detail_instruction}
    
    Include:
    1. Overall purpose and functionality
    2. Detailed function/class documentation with parameters and return values
    3. Code structure overview
    4. Dependencies and requirements
    5. Usage examples where appropriate
    6. Potential issues or areas for improvement
    
    {language_specific}
    
    File: {file_path}
    
    ```{language.lower()}
    {content}
    ```
    
    Format the documentation in clean, well-structured markdown.
    """

    try:
        response = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=max_tokens,
            temperature=DEFAULT_TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except Exception as e:
        return f"Error generating documentation: {str(e)}"


def generate_project_overview(
    files: Dict[str, Dict[str, Any]], client: anthropic.Anthropic
) -> str:
    """
    Generate a project-level overview based on all files, recognizing directory structure.

    Args:
        files: Dictionary mapping file paths to their info
        client: Anthropic client instance

    Returns:
        Generated project overview text
    """
    # Organize files by directory
    dir_structure = {}
    for file_path, file_info in files.items():
        dir_path = file_info.get("directory", "")
        if dir_path not in dir_structure:
            dir_structure[dir_path] = []
        dir_structure[dir_path].append((file_path, file_info["language"]))

    # Build directory-based file listing
    file_summaries = []
    for dir_path, files_in_dir in sorted(dir_structure.items()):
        if dir_path:
            file_summaries.append(f"\n**Directory: {dir_path}/**")
        else:
            file_summaries.append("\n**Root Directory:**")

        for file_path, language in sorted(files_in_dir):
            file_name = os.path.basename(file_path)
            file_summaries.append(f"  - {file_name} ({language})")

    file_list = "\n".join(file_summaries)

    prompt = f"""
    Please generate a project overview based on the following list of files in the codebase.
    Create a summary that discusses the likely purpose of the project, its structure,
    and how the files might relate to each other.
    
    Pay special attention to the directory structure and how it reflects the project's architecture.
    Consider what different directories might represent in terms of functionality or components.
    
    Project file structure:
    {file_list}
    
    Format your response as a comprehensive markdown document with appropriate headings and structure.
    Include sections for:
    1. Project Purpose
    2. Architecture Overview
    3. Key Components
    4. Directory Structure Analysis
    5. Potential Dependencies and Technologies
    """

    try:
        response = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=3000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except Exception as e:
        return f"Error generating project overview: {str(e)}"
