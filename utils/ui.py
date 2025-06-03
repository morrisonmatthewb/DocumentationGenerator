"""
User interface components and display functions.
"""

import os
import time
import json
import streamlit as st
from typing import Dict, List, Any, Tuple, Optional
from dotenv import load_dotenv

from config.constants import (
    SUPPORTED_EXTENSIONS,
    SUPPORTED_ARCHIVE_FORMATS,
    DOC_LEVELS,
    DEFAULT_DOC_LEVEL,
    MAX_FILE_SIZE_RANGE,
    DEFAULT_MAX_FILE_SIZE_MB,
    APP_CSS,
    MERMAID_SCRIPT,
)
from utils.documentation import build_combined_documentation
from utils.html import convert_markdown_to_html

# Load environment variables
load_dotenv()


def setup_page():
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title="Advanced Documentation Generator", page_icon="📚", layout="wide"
    )

    # Apply custom styling
    st.markdown(
        f"""
    <style>
    {APP_CSS}
    </style>
    {MERMAID_SCRIPT}
    """,
        unsafe_allow_html=True,
    )


def get_api_key_ui() -> Optional[str]:
    """
    Get the API key from environment, Streamlit secrets, or user input.
    UI-specific version to avoid circular imports.

    Returns:
        API key string or None if not available
    """
    # Try environment variable first
    api_key = os.getenv("ANTHROPIC_API_KEY")

    # Print the environment variable for debugging (remove in production)
    if api_key:
        st.sidebar.success("API key loaded from environment")

    # Check session state if environment variable is not available
    if not api_key and "anthropic_api_key" in st.session_state:
        api_key = st.session_state.anthropic_api_key
        st.sidebar.info("API key loaded from session state")

    # If still no API key, ask user
    if not api_key:
        api_key = st.text_input(
            "Enter your Anthropic API Key:",
            type="password",
            help="Your API key will be stored for this session only",
        )
        if api_key:
            st.session_state.anthropic_api_key = api_key

    return api_key


def sidebar_config() -> Dict[str, Any]:
    """Configure and display the sidebar options.

    Returns:
        Dictionary containing all configuration options
    """
    st.sidebar.header("Configuration")

    # API key input
    api_key = get_api_key_ui()

    # Documentation level selection
    doc_level = st.sidebar.radio(
        "Documentation Detail Level:",
        DOC_LEVELS,
        index=DOC_LEVELS.index(DEFAULT_DOC_LEVEL),
    )

    # File type selection
    st.sidebar.subheader("File Types to Process")
    selected_extensions = []
    for ext, lang in SUPPORTED_EXTENSIONS.items():
        if st.sidebar.checkbox(f"{lang} ({ext})", value=True):
            selected_extensions.append(ext)

    # File size limit
    max_file_size = st.sidebar.slider(
        "Maximum file size (MB)",
        min_value=MAX_FILE_SIZE_RANGE[0],
        max_value=MAX_FILE_SIZE_RANGE[1],
        value=DEFAULT_MAX_FILE_SIZE_MB,
        help="Files larger than this will be skipped",
    )

    # Project overview option
    generate_overview = st.sidebar.checkbox("Generate Project Overview", value=True)

    # Directory structure visualization
    generate_dir_structure = st.sidebar.checkbox(
        "Generate Directory Structure Visualization", value=True
    )

    return {
        "api_key": api_key,
        "doc_level": doc_level,
        "selected_extensions": selected_extensions,
        "max_file_size": max_file_size,
        "generate_overview": generate_overview,
        "generate_dir_structure": generate_dir_structure,
    }


def file_uploader_section() -> Tuple[Optional[Any], Optional[str], Optional[str]]:
    """Display the file uploader and process the uploaded file.

    Returns:
        Tuple of (uploaded_file, file_extension, archive_format)
    """
    accepted_formats = list(SUPPORTED_ARCHIVE_FORMATS.keys())
    upload_label = "Choose an archive file ({})".format(", ".join(accepted_formats))

    uploaded_file = st.file_uploader(upload_label, type=accepted_formats)

    if uploaded_file is not None:
        # Get archive format for display
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        # Handle special cases like .tar.gz
        if ".tar." in uploaded_file.name.lower():
            file_extension = "." + ".".join(uploaded_file.name.split(".")[-2:])

        archive_format = SUPPORTED_ARCHIVE_FORMATS.get(file_extension, "Unknown")

        return uploaded_file, file_extension, archive_format

    return None, None, None


def display_file_summary(files: Dict[str, Dict[str, Any]]) -> bool:
    """Display summary information about the extracted files.

    Args:
        files: Dictionary of extracted files

    Returns:
        Boolean indicating if valid files were found
    """
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"Found {len(files)} code files")

        # Count files by language
        language_counts = {}
        for file_info in files.values():
            lang = file_info["language"]
            language_counts[lang] = language_counts.get(lang, 0) + 1

        for lang, count in sorted(language_counts.items()):
            st.write(f"- {lang}: {count} files")

    with col2:
        if not files:
            st.warning("No supported code files found in the archive.")
            return False
        else:
            # Find all unique directories
            directories = set()
            for file_path, file_info in files.items():
                dir_path = file_info.get("directory", "")
                if dir_path:
                    directories.add(dir_path)

            num_dirs = len(directories)
            if num_dirs > 0:
                st.write(f"Project contains {num_dirs} directories")

            # List files found by directory
            with st.expander("Files found (organized by directory)"):
                # Display root files first
                root_files = [
                    path for path, info in files.items() if not info.get("directory")
                ]
                if root_files:
                    st.markdown("**Root Directory:**")
                    for file_path in sorted(root_files):
                        file_name = os.path.basename(file_path)
                        st.code(file_name, language="bash")

                # Then display each directory
                for directory in sorted(directories):
                    st.markdown(f"**{directory}/**")
                    dir_files = [
                        path
                        for path, info in files.items()
                        if info.get("directory") == directory
                    ]
                    for file_path in sorted(dir_files):
                        file_name = os.path.basename(file_path)
                        st.code(file_name, language="bash")

            return True


def display_documentation_progress(current: int, total: int, file_path: str):
    """Display progress during documentation generation.

    Args:
        current: Current file index
        total: Total number of files
        file_path: Current file being processed
    """
    progress = st.progress((current) / total)
    st.write(f"Generating documentation for: {file_path}")


def display_documentation(documentation: Dict[str, str]):
    """Display the generated documentation.

    Args:
        documentation: Dictionary of generated documentation
    """
    st.subheader("Generated Documentation")

    # Show directory structure first if it exists
    if "__directory_structure__" in documentation:
        with st.expander("Directory Structure", expanded=True):
            st.markdown(documentation["__directory_structure__"])

    # Show interactive diagram if it exists
    if "__mermaid_diagram__" in documentation:
        with st.expander("Interactive Directory Graph", expanded=False):
            st.markdown(documentation["__mermaid_diagram__"], unsafe_allow_html=True)

    # Show project overview next if it exists
    if "__project_overview__" in documentation:
        with st.expander("Project Overview", expanded=True):
            st.markdown(documentation["__project_overview__"])

    # Then show individual file documentation
    for file_path, doc in documentation.items():
        if file_path not in [
            "__project_overview__",
            "__directory_structure__",
            "__mermaid_diagram__",
        ]:
            with st.expander(f"Documentation for {file_path}"):
                st.markdown(doc)


def display_download_options(documentation: Dict[str, str], key_suffix: str = ""):
    """Display download options for the documentation.

    Args:
        documentation: Dictionary of generated documentation
        key_suffix: Suffix for widget keys to avoid duplicates
    """
    st.subheader("Download Options")

    # Create combined documentation
    combined_docs = build_combined_documentation(documentation)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            label="Download as Markdown",
            data=combined_docs,
            file_name="documentation.md",
            mime="text/markdown",
            key=f"download_markdown{key_suffix}",
        )

    with col2:
        # Download as JSON for programmatic use
        json_data = json.dumps(documentation, indent=2)
        st.download_button(
            label="Download as JSON",
            data=json_data,
            file_name="documentation.json",
            mime="application/json",
            key=f"download_json{key_suffix}",
        )

    with col3:
        # Generate and download html
        try:
            with st.spinner("Generating html file..."):
                output_data = convert_markdown_to_html(
                    combined_docs, title="Project Documentation"
                )

                file_name = "documentation.html"
                mime_type = "text/html"
                button_label = "Download as HTML"

            st.download_button(
                label=button_label,
                data=output_data,
                file_name=file_name,
                mime=mime_type,
                key=f"download_pdf{key_suffix}",
            )
        except Exception as e:
            st.error(f"Error generating document: {str(e)}")


def display_generation_time(start_time: float):
    """Display the time taken to generate documentation.

    Args:
        start_time: Start time in seconds since epoch
    """
    end_time = time.time()
    processing_time = end_time - start_time
    st.success(f"Documentation generated in {processing_time:.2f} seconds")
