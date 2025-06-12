"""
Documentation generation and processing utilities.
"""

from typing import Dict, Any
from collections import defaultdict


def build_combined_documentation(documentation: Dict[str, Any]) -> str:
    """
    Build a single combined documentation file from individual file documentation.
    
    Args:
        documentation: Dictionary mapping file paths to documentation content
        
    Returns:
        Combined documentation text in Markdown format
    """
    combined_docs = ""
    
    # Include directory structure first if it exists
    if "__directory_structure__" in documentation:
        combined_docs += documentation['__directory_structure__'] + "\n\n---\n\n"
    
    # Then include project overview
    if "__project_overview__" in documentation:
        # combined_docs += f"# Project Overview\n\n{documentation['__project_overview__']}\n\n---\n\n" # Includes section title, redundant
        combined_docs += f"{documentation['__project_overview__']}\n\n---\n\n"
    

    root_files = []
    non_root_files = []
    for file_path, doc in documentation.items():
        if file_path not in ["__project_overview__", "__directory_structure__", "__mermaid_diagram__"]:
            dirs = file_path.split("/")
            if len(dirs) == 1:
                root_files.append((file_path, doc))
            else:
                non_root_files.append((file_path, doc))

    sorted_non_root_files = sorted(non_root_files)
    for _, doc in root_files:
        combined_docs += f"# Documentation for {file_path}\n\n{doc}\n\n---\n\n"
    for _, doc in sorted_non_root_files:
        combined_docs += f"# Documentation for {file_path}\n\n{doc}\n\n---\n\n"
    return combined_docs
"""
    # Add each file's documentation
    for file_path, doc in documentation.items():
        if file_path not in ["__project_overview__", "__directory_structure__", "__mermaid_diagram__"]:
            # combined_docs += f"# Documentation for {file_path}\n\n{doc}\n\n---\n\n" # Includes section title, redundant
            combined_docs += f"{doc}\n\n---\n\n"
 
    return combined_docs
"""