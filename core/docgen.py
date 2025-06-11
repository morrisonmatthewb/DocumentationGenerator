"""
Core documentation generation functionality.
"""

import time
import streamlit as st

from utils.api import (
    initialize_client,
    generate_project_overview,
    generate_documentation,
    generate_content_based_overview,
)
from utils.archive import extract_files_from_archive
from utils.visualization import build_directory_tree
from utils.ui import display_generation_time
from core.concurrent_docgen import process_archive

def generate_all_documentation(files, config):
    """
    Generate documentation for all files and project overview.

    Args:
        files: Dictionary of extracted files
        config: Configuration dictionary

    Returns:
        Dictionary containing all generated documentation
    """
    documentation = {}
    start_time = time.time()

    # Initialize client
    try:
        client = initialize_client(config["api_key"])
    except Exception as e:
        st.error(f"Failed to initialize Claude client: {str(e)}")
        return None

    # Generate directory structure visualization if selected
    if config["generate_dir_structure"] and len(files) > 1:
        with st.spinner("Generating directory structure visualization..."):
            tree, ascii_tree, mermaid_code = build_directory_tree(files)

            # Store both visualizations
            documentation["__directory_structure__"] = ascii_tree

            # Also create a separate entry for the Mermaid diagram
            documentation["__mermaid_diagram__"] = f"""
    # Project Directory Structure (Interactive)
    
    ```mermaid
    {mermaid_code}
    ```
    """

    # Process each fileAdd commentMore actions
    total_files = len(files)
    for i, (file_path, file_info) in enumerate(files.items()):
        documentation[file_path] = generate_documentation(
            file_path, file_info, client, config["doc_level"]
        )
    # Generate project overview if selected
    if config["generate_overview"] and len(files) > 1:
        with st.spinner("Generating project overview..."):
            documentation["__project_overview__"] = generate_content_based_overview(
                documentation, files, client
            )
    # Display generation time
    display_generation_time(start_time)

    return documentation
