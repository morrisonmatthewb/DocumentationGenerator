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
    FILE_TYPE_CATEGORIES,
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
from utils.demo import get_api_key_ui_for_demo, display_demo_status_sidebar
from utils.api import is_valid_api_key, simple_get_api_key


# Load environment variables
load_dotenv()


def setup_page():
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title="Documentation Generator", page_icon="📚", layout="wide"
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
    """Get and validate api key

    Returns:
        Anthropic API key or Empty String
    """

    api_key = get_api_key_ui_for_demo()
    return api_key


def sidebar_config() -> Dict[str, Any]:
    """Configure and display the sidebar options with categorized file types.

    Returns:
        Dictionary containing all configuration options
    """
    st.sidebar.header("Configuration")

    # Display demo status
    # display_demo_status_sidebar()

    # Documentation level selection
    doc_level = st.sidebar.radio(
        "Documentation Detail Level:",
        DOC_LEVELS,
        index=DOC_LEVELS.index(DEFAULT_DOC_LEVEL),
    )

    # File type selection with categories
    st.sidebar.subheader("File Types to Process")

    # Add "Select All" / "Deselect All" buttons
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("✅ All", key="select_all", help="Select all file types"):
            for category, files in FILE_TYPE_CATEGORIES.items():
                for ext, _ in files:
                    st.session_state[f"file_type_{ext}"] = True

    with col2:
        if st.button("❌ None", key="deselect_all", help="Deselect all file types"):
            for category, files in FILE_TYPE_CATEGORIES.items():
                for ext, _ in files:
                    st.session_state[f"file_type_{ext}"] = False

    # Category-based file type selection
    selected_extensions = []

    for category, file_types in FILE_TYPE_CATEGORIES.items():
        with st.sidebar.expander(f"📁 {category}", expanded=False):
            # Add category-level select/deselect
            cat_col1, cat_col2 = st.columns(2)

            with cat_col1:
                if st.button(
                    "✅", key=f"select_cat_{category}", help=f"Select all {category}"
                ):
                    for ext, _ in file_types:
                        st.session_state[f"file_type_{ext}"] = True

            with cat_col2:
                if st.button(
                    "❌",
                    key=f"deselect_cat_{category}",
                    help=f"Deselect all {category}",
                ):
                    for ext, _ in file_types:
                        st.session_state[f"file_type_{ext}"] = False

            # Individual file type checkboxes
            for ext, lang in file_types:
                # Use session state to persist checkbox states
                checkbox_key = f"file_type_{ext}"
                default_value = st.session_state.get(
                    checkbox_key, True
                )  # Default to True

                if st.checkbox(
                    f"{lang} ({ext})",
                    value=default_value,
                    key=checkbox_key,
                    help=f"Include {lang} files in documentation generation",
                ):
                    selected_extensions.append(ext)

    # Display selection summary
    if selected_extensions:
        st.sidebar.success(f"✅ {len(selected_extensions)} file types selected")
    else:
        st.sidebar.warning("⚠️ No file types selected")

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

    # Performance settings
    st.sidebar.subheader("Performance Settings")
    concurrency_method = st.sidebar.radio(
        "Processing Method:",
        ["Sequential", "Batch Processing", "Full Concurrent"],
        index=1,  # Default to Batch Processing
        help="Choose how to process multiple files.\nBatch Processing is recommended for all use cases.\nFull Concurrent is marginally faster for larger projects but may cause issues currently.",
    )

    # API key input
    api_key = simple_get_api_key()
    if not api_key:
        st.info("👆 Please enter a valid API key above to continue")
        st.stop()

    # Initialize the config dictionary
    config = {
        "api_key": api_key,
        "doc_level": doc_level,
        "selected_extensions": selected_extensions,
        "max_file_size": max_file_size,
        "generate_overview": generate_overview,
        "generate_dir_structure": generate_dir_structure,
        "concurrency_method": concurrency_method,
    }

    # Add method-specific options
    if concurrency_method == "Batch Processing":
        config["batch_size"] = st.sidebar.slider(
            "Batch Size",
            min_value=2,
            max_value=5,
            value=3,
            help="Number of files to process simultaneously in each batch",
        )
    elif concurrency_method == "Full Concurrent":
        config["max_workers"] = st.sidebar.slider(
            "Max Workers",
            min_value=2,
            max_value=8,
            value=3,
            help="Maximum number of concurrent threads (keep low to avoid API issues)",
        )

    return config


def display_file_summary_enhanced(files: Dict[str, Dict[str, Any]]) -> bool:
    """Enhanced file summary with categorized breakdown.

    Args:
        files: Dictionary of extracted files

    Returns:
        Boolean indicating if valid files were found
    """
    if not files:
        st.warning("No supported code files found in the archive.")
        return False

    col1, col2 = st.columns(2)

    with col1:
        st.success(f"Found {len(files)} code files")

        # Count files by language and categorize
        language_counts = {}
        category_counts = {}

        for file_info in files.values():
            lang = file_info["language"]
            language_counts[lang] = language_counts.get(lang, 0) + 1

            # Find which category this language belongs to
            file_ext = None
            for ext, language in SUPPORTED_EXTENSIONS.items():
                if language == lang:
                    file_ext = ext
                    break

            if file_ext:
                for category, file_types in FILE_TYPE_CATEGORIES.items():
                    if any(ext == file_ext for ext, _ in file_types):
                        category_counts[category] = category_counts.get(category, 0) + 1
                        break

        # Display by category
        st.write("**Files by Category:**")
        for category, count in sorted(category_counts.items()):
            st.write(f"📁 {category}: {count} files")

        # Show top languages
        st.write("**Top Languages:**")
        top_languages = sorted(
            language_counts.items(), key=lambda x: x[1], reverse=True
        )[:5]
        for lang, count in top_languages:
            st.write(f"• {lang}: {count} files")

        if len(language_counts) > 5:
            st.write(f"... and {len(language_counts) - 5} more languages")

    with col2:
        # Find all unique directories
        directories = set()
        for file_path, file_info in files.items():
            dir_path = file_info.get("directory", "")
            if dir_path:
                directories.add(dir_path)

        num_dirs = len(directories)
        if num_dirs > 0:
            st.write("**Project Structure:**")
            st.write(f"📂 {num_dirs} directories")
            st.write(f"📄 {len(files)} files")

        # List files found by directory
        with st.expander("📋 Detailed File List", expanded=False):
            # Display root files first
            root_files = [
                path for path, info in files.items() if not info.get("directory")
            ]
            if root_files:
                st.markdown("**📁 Root Directory:**")
                for file_path in sorted(root_files):
                    file_name = os.path.basename(file_path)
                    file_info = files[file_path]
                    st.write(f"• `{file_name}` ({file_info['language']})")

            # Then display each directory
            for directory in sorted(directories):
                st.markdown(f"**📁 {directory}/**")
                dir_files = [
                    path
                    for path, info in files.items()
                    if info.get("directory") == directory
                ]
                for file_path in sorted(dir_files):
                    file_name = os.path.basename(file_path)
                    file_info = files[file_path]
                    st.write(f"• `{file_name}` ({file_info['language']})")

    return True


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
                # Display root files
                root_files = [
                    path for path, info in files.items() if not info.get("directory")
                ]
                if root_files:
                    st.markdown("**Root Directory:**")
                    for file_path in sorted(root_files):
                        file_name = os.path.basename(file_path)
                        st.code(file_name, language="bash")

                # Display each directory
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
    """Display download options for the documentation."""
    st.subheader("Download Options")

    # Create combined documentation
    combined_docs = build_combined_documentation(documentation)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            label="📥 Download as Markdown",
            data=combined_docs,
            file_name="documentation.md",
            mime="text/markdown",
            key=f"download_markdown{key_suffix}",
            help="Download as Markdown file",
        )

    with col2:
        json_data = json.dumps(documentation, indent=2)
        st.download_button(
            label="📥 Download as JSON",
            data=json_data,
            file_name="documentation.json",
            mime="application/json",
            key=f"download_json{key_suffix}",
            help="Download as JSON file for programmatic use",
        )

    with col3:
        try:
            html_content = convert_markdown_to_html(
                combined_docs, title="Project Documentation"
            )

            st.download_button(
                label="📥 Download as HTML",
                data=html_content,
                file_name="documentation.html",
                mime="text/html",
                key=f"download_html{key_suffix}",
                help="Download as interactive HTML file",
            )
        except Exception as e:
            st.error(f"Error generating HTML: {str(e)}")

    # Show save confirmation if this is a new generation
    if key_suffix == "_current":
        st.info(
            "💾 This documentation has been automatically saved to your session history!"
        )


def display_generation_time(start_time: float):
    """Display the time taken to generate documentation.

    Args:
        start_time: Start time in seconds since epoch
    """
    end_time = time.time()
    processing_time = end_time - start_time
    st.success(f"Documentation generated in {processing_time:.2f} seconds")
