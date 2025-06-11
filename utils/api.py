"""
Claude API integration utilities.
"""

import os
import anthropic
import streamlit as st
from config.constants import (
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    BASIC_LEVEL_MAX_TOKENS,
    COMPREHENSIVE_LEVEL_MAX_TOKENS,
    EXPERT_LEVEL_MAX_TOKENS,
    PROJECT_OVERVIEW_MAX_TOKENS,
)
from typing import Dict, Any, Optional, List, Tuple
from dotenv import load_dotenv
import re


# Load environment variables
load_dotenv()


def _is_valid_api_key(api_key: str) -> bool:
    if not api_key:
        return False

    demo_pw = os.getenv("DEMO_PW")
    api_key = api_key.strip()

    # Allow demo mode
    if api_key.lower() == demo_pw and _check_is_demo_key_valid():
        return True

    # Check Anthropic format
    pattern = r"^sk-ant-api03-[a-zA-Z0-9_-]{95}$"
    return bool(re.match(pattern, api_key))


def _check_is_demo_key_valid() -> bool:
    pattern = r"^sk-ant-api03-[a-zA-Z0-9_-]{95}$"
    return bool(re.match(pattern, os.getenv("DEMO_KEY")))


def _invalid_api_key_error_message():
    st.error("Invalid API key. Please check your key.")


def _check_api_input(user_input) -> Optional[str]:
    if not user_input:
        _invalid_api_key_error_message()
        return None

    demo_pw = os.getenv("DEMO_PW")

    # Validate input
    if _is_valid_api_key(user_input):
        if user_input.lower() == demo_pw:
            st.success("Demo mode activated.")
            st.session_state.anthropic_api_key = demo_pw
            return os.getenv("DEMO_KEY")
        else:
            st.success("Valid API key.")
            st.session_state.anthropic_api_key = user_input
            return user_input
    else:
        _invalid_api_key_error_message()
        return None


def get_api_key() -> Optional[str]:
    """API key input with validation."""

    api_key = os.getenv("ANTHROPIC_API_KEY")
    demo_pw = os.getenv("DEMO_PW")
    if api_key and _is_valid_api_key(api_key):
        st.success("API key loaded from environment")
        return api_key

    api_input = _check_api_input(st.session_state.api_key_input)
    if not api_input:
        # Get key from session
        if "anthropic_api_key" in st.session_state:
            api_key = st.session_state.anthropic_api_key
            if api_key == demo_pw and _check_is_demo_key_valid():
                st.warning("Demo Key loaded from session")
                return os.getenv("DEMO_KEY")
            if _is_valid_api_key(api_key):
                st.warning("API Key loaded from session")
                return api_key
    return api_input


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
        max_tokens = BASIC_LEVEL_MAX_TOKENS
    elif doc_level == "expert":
        detail_instruction = "Provide extremely detailed documentation with advanced insights and best practices."
        max_tokens = EXPERT_LEVEL_MAX_TOKENS
    else:
        detail_instruction = (
            "Provide comprehensive documentation with a good balance of detail."
        )
        max_tokens = COMPREHENSIVE_LEVEL_MAX_TOKENS

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
        if os.getenv("DEBUG") == "true":
            st.warning("calling api in gen doc")
        return response.content[0].text
    except Exception as e:
        return f"Error generating documentation: {str(e)}"


def generate_project_overview(
    files: Dict[str, Dict[str, Any]], client: anthropic.Anthropic
) -> str:
    """
    Generate a project-level overview based on all files, recognizing directory structure.
    Old approach, generate_content_based_overview is improved version of this.

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
            max_tokens=PROJECT_OVERVIEW_MAX_TOKENS,
            temperature=DEFAULT_TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
        )
        if os.getenv("DEBUG") == "true":
            st.warning("calling api in gen overview")
        return response.content[0].text
    except Exception as e:
        return f"Error generating project overview: {str(e)}"


def generate_content_based_overview(
    documentation: Dict[str, str],
    files: Dict[str, Dict[str, Any]],
    client: anthropic.Anthropic,
) -> str:
    """
    Generate project overview based on actual documentation content.
    Handles large content by chunking and summarization.

    Args:
        documentation: Dictionary of generated documentation (file_path -> documentation)
        files: Original file structure info
        client: Anthropic client instance

    Returns:
        Generated project overview text
    """
    # Filter out special entries (overview, structure, etc.)
    file_docs = {
        path: doc for path, doc in documentation.items() if not path.startswith("__")
    }

    if not file_docs:
        return "No file documentation available for overview generation."

    # Check total content size and decide strategy
    total_content = "\n\n".join(file_docs.values())
    estimated_tokens = len(total_content) // 3  # Rough estimate: 1 token ≈ 3 chars
    if not st.session_state.force_content_overview:
        if estimated_tokens < 15000:  # Small project - use all content
            return _generate_overview_direct(file_docs, files, client)
        elif estimated_tokens < 50000:  # Medium project - use summaries
            return _generate_overview_with_summaries(file_docs, files, client)
        else:  # Large project - use hierarchical approach
            return _generate_overview_hierarchical(file_docs, files, client)
    else:
        return _generate_overview_direct(file_docs, files, client)


def _generate_overview_direct(
    file_docs: Dict[str, str],
    files: Dict[str, Dict[str, Any]],
    client: anthropic.Anthropic,
) -> str:
    """Direct overview generation for small projects."""

    # Organize content by directory
    dir_structure = _organize_docs_by_directory(file_docs, files)

    # Build content for prompt
    content_sections = []
    for dir_path, docs in dir_structure.items():
        if dir_path:
            content_sections.append(f"\n## Directory: {dir_path}/\n")
        else:
            content_sections.append(f"\n## Root Directory\n")

        for file_path, doc_content in docs:
            file_name = os.path.basename(file_path)
            # Truncate very long docs to keep within limits
            truncated_doc = _truncate_content(doc_content, 1000)
            content_sections.append(f"### {file_name}\n{truncated_doc}\n")

    combined_content = "\n".join(content_sections)

    prompt = f"""
    Generate a comprehensive project overview based on the following detailed documentation 
    for each file in the codebase. Use the actual documentation content to understand the 
    project's purpose, architecture, and functionality.
    
    {combined_content}
    
    Based on this documentation, create a project overview with:
    1. **Project Purpose** - What this project does and its main goals
    2. **Architecture Overview** - How components work together
    3. **Key Features** - Main functionality based on the documented code
    4. **Technical Stack** - Technologies, frameworks, and patterns used
    5. **Component Relationships** - How different parts interact
    6. **Notable Implementation Details** - Interesting technical aspects
    7. **Potential Improvements** - Areas of the project that may be messy, sub-optimal, or against industry standard software engineering principles. Only add this section if there is an obvious or recurring issue.
    
    Format as a well-structured markdown document. Focus on insights that can only 
    be gained from reading the actual code documentation, not just file names.
    """

    try:
        response = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=PROJECT_OVERVIEW_MAX_TOKENS,
            temperature=DEFAULT_TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except Exception as e:
        return f"Error generating content-based overview: {str(e)}"


def _generate_overview_with_summaries(
    file_docs: Dict[str, str],
    files: Dict[str, Dict[str, Any]],
    client: anthropic.Anthropic,
) -> str:
    """Generate overview using file summaries for medium projects."""

    # First, generate summaries for each file
    file_summaries = {}

    for file_path, doc_content in file_docs.items():
        summary = _generate_file_summary(file_path, doc_content, client)
        file_summaries[file_path] = summary

    # Organize summaries by directory
    dir_structure = _organize_docs_by_directory(file_summaries, files)

    # Build content for overview prompt
    summary_sections = []
    for dir_path, summaries in dir_structure.items():
        if dir_path:
            summary_sections.append(f"\n## Directory: {dir_path}/\n")
        else:
            summary_sections.append(f"\n## Root Directory\n")

        for file_path, summary in summaries:
            file_name = os.path.basename(file_path)
            summary_sections.append(f"**{file_name}**: {summary}")

    combined_summaries = "\n".join(summary_sections)

    prompt = f"""
    Generate a comprehensive project overview based on these file-by-file summaries 
    of the project's documentation:
    
    {combined_summaries}
    
    Create a high-level project overview that synthesizes these individual file summaries into:
    1. **Project Purpose** - Overall goal and domain
    2. **System Architecture** - How components fit together
    3. **Core Functionality** - Main features and capabilities
    4. **Technology Stack** - Frameworks, libraries, and patterns
    5. **Data Flow** - How information moves through the system
    6. **Key Design Patterns** - Architectural approaches used
    
    Focus on the big picture and relationships between components rather than 
    individual file details.
    """

    try:
        response = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=PROJECT_OVERVIEW_MAX_TOKENS,
            temperature=DEFAULT_TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except Exception as e:
        return f"Error generating summary-based overview: {str(e)}"


def _generate_overview_hierarchical(
    file_docs: Dict[str, str],
    files: Dict[str, Dict[str, Any]],
    client: anthropic.Anthropic,
) -> str:
    """Generate overview using hierarchical approach for large projects."""

    # Step 1: Group files by directory and generate directory summaries
    dir_structure = _organize_docs_by_directory(file_docs, files)
    directory_summaries = {}

    for dir_path, docs in dir_structure.items():
        dir_name = dir_path if dir_path else "Root"
        dir_summary = _generate_directory_summary(dir_name, docs, client)
        directory_summaries[dir_name] = dir_summary

    # Step 2: Generate high-level overview from directory summaries
    dir_summary_text = "\n\n".join(
        [
            f"**{dir_name}**: {summary}"
            for dir_name, summary in directory_summaries.items()
        ]
    )

    prompt = f"""
    Generate a high-level project overview based on these directory-level summaries:
    
    {dir_summary_text}
    
    Create an executive-level project overview that covers:
    1. **Project Mission** - What problem this solves
    2. **System Architecture** - Major components and their roles
    3. **Technical Approach** - Key technologies and methodologies
    4. **Feature Overview** - Main capabilities and functions
    5. **Integration Points** - How different parts connect
    6. **Scalability & Design** - Architectural decisions and patterns
    
    This should be a high-level strategic overview suitable for stakeholders 
    who want to understand the project's scope and approach.
    """

    try:
        response = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=PROJECT_OVERVIEW_MAX_TOKENS,
            temperature=DEFAULT_TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except Exception as e:
        return f"Error generating hierarchical overview: {str(e)}"


def _generate_file_summary(
    file_path: str, doc_content: str, client: anthropic.Anthropic
) -> str:
    """Generate a concise summary of a file's documentation."""

    truncated_content = _truncate_content(doc_content, 2000)

    prompt = f"""
    Summarize the following file documentation in 2-3 sentences. Focus on:
    - What this file does (purpose/responsibility)
    - Key functions/classes it contains
    - How it fits into the larger system
    
    File: {os.path.basename(file_path)}
    Documentation:
    {truncated_content}
    
    Provide a concise summary:
    """

    try:
        response = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=300,
            temperature=DEFAULT_TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except Exception as e:
        return f"Summary generation failed for {file_path}"


def _generate_directory_summary(
    dir_name: str, docs: List[Tuple[str, str]], client: anthropic.Anthropic
) -> str:
    """Generate a summary for a directory based on its files' documentation."""

    file_summaries = []
    for file_path, doc_content in docs:
        file_name = os.path.basename(file_path)
        truncated_doc = _truncate_content(doc_content, 500)
        file_summaries.append(f"**{file_name}**: {truncated_doc}")

    combined_content = "\n".join(file_summaries)

    prompt = f"""
    Summarize the purpose and functionality of the "{dir_name}" directory based on 
    its files' documentation. Focus on:
    - What this directory's role is in the project
    - Main functionality it provides
    - How files work together within this directory
    
    Files in {dir_name}:
    {combined_content}
    
    Provide a 3-4 sentence directory summary:
    """

    try:
        response = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=300,
            temperature=DEFAULT_TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except Exception as e:
        return f"Directory summary generation failed for {dir_name}"


def _organize_docs_by_directory(
    docs: Dict[str, str], files: Dict[str, Dict[str, Any]]
) -> Dict[str, List[Tuple[str, str]]]:
    """Organize documentation by directory structure."""

    dir_structure = {}

    for file_path, doc_content in docs.items():
        # Get directory from original file info
        dir_path = files.get(file_path, {}).get("directory", "")

        if dir_path not in dir_structure:
            dir_structure[dir_path] = []

        dir_structure[dir_path].append((file_path, doc_content))

    return dir_structure


def _truncate_content(content: str, max_chars: int) -> str:
    """Truncate content to maximum character count with smart truncation."""

    if len(content) <= max_chars:
        return content

    # Try to truncate at a sentence boundary
    truncated = content[:max_chars]
    last_period = truncated.rfind(".")
    last_newline = truncated.rfind("\n")

    # Use the later of the two boundaries
    boundary = max(last_period, last_newline)

    if boundary > max_chars * 0.7:  # Only use boundary if it's not too short
        return truncated[: boundary + 1] + "\n\n[Content truncated...]"
    else:
        return truncated + "\n\n[Content truncated...]"
