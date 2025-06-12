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
        combined_docs += documentation["__directory_structure__"] + "\n\n---\n\n"

    # Then include project overview
    if "__project_overview__" in documentation:
        # combined_docs += f"# Project Overview\n\n{documentation['__project_overview__']}\n\n---\n\n" # Includes section title, redundant
        combined_docs += f"{documentation['__project_overview__']}\n\n---\n\n"

    for file_path, doc in documentation.items():
        if file_path not in [
            "__project_overview__",
            "__directory_structure__",
            "__mermaid_diagram__",
        ]:
            combined_docs += f"{doc}\n\n---\n\n"
    return combined_docs


def organize_documentation_by_dir(documentation):
    """
    Organize documentation by directory to be displayed in expected format.

    Args:
        documentation: Dictionary mapping file paths to documentation content

    Returns:
        Dict[str, Any] reorganized such that root files come first, then the rest sorted alphabetically by their parent directory
    """
    if not documentation:
        return None

    organized_doc = {}
    path_dict = defaultdict(list)
    for file_path, doc in documentation.items():
        dirs = file_path.split("/")
        if len(dirs) == 1:
            organized_doc[file_path] = doc
        else:
            path_dict["".join(dirs[:-1])].append((file_path, doc))
    sorted_documentation = defaultdict(list, sorted(path_dict.items()))
    for _, files in sorted_documentation.items():
        for file_path, doc in files:
            organized_doc[file_path] = doc

    return organized_doc
