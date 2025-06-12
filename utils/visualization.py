"""
Directory structure visualization utilities.
"""

import os
from collections import defaultdict
from typing import Dict, List, Tuple, Any


def build_directory_tree(files: Dict[str, Dict[str, Any]]) -> Tuple[Dict, str, str]:
    """
    Build a nested directory tree structure from the list of files.

    Args:
        files: Dictionary mapping file paths to file info

    Returns:
        Tuple of (tree structure, ASCII tree visualization, Mermaid diagram code)
    """
    # Create nested directory structure
    tree = defaultdict(list)
    for file_path, file_info in files.items():
        dir_path = file_info.get("directory", "")
        file_name = os.path.basename(file_path)

        if dir_path:
            tree[dir_path].append((file_name, file_info["language"]))
        else:
            tree["root"].append((file_name, file_info["language"]))

    # Build hierarchical structure for ASCII tree
    def build_tree_structure():
        structure = {}

        # Add all directories to structure
        all_dirs = set()
        for dir_path in tree.keys():
            if dir_path != "root":
                # Add all parent directories
                parts = dir_path.split("/")
                for i in range(len(parts)):
                    current_path = "/".join(parts[: i + 1])
                    all_dirs.add(current_path)

        # Initialize structure
        structure[""] = {"dirs": set(), "files": []}  # Root level
        for dir_path in all_dirs:
            structure[dir_path] = {"dirs": set(), "files": []}

        # Populate directory relationships
        for dir_path in all_dirs:
            if "/" in dir_path:
                parent = "/".join(dir_path.split("/")[:-1])
                structure[parent]["dirs"].add(dir_path.split("/")[-1])
            else:
                structure[""]["dirs"].add(dir_path)

        # Add files to their directories
        for dir_path, file_list in tree.items():
            if dir_path == "root":
                structure[""]["files"] = file_list
            else:
                structure[dir_path]["files"] = file_list

        return structure

    def generate_ascii_tree(structure, path="", prefix="", is_last=True):
        """Recursively generate ASCII tree"""
        lines = []

        # Get current directory info
        current = structure[path]
        dirs = sorted(current["dirs"])
        files = sorted(current["files"])

        # Process directories first
        for i, dir_name in enumerate(dirs):
            is_last_dir = (i == len(dirs) - 1) and len(files) == 0

            # Add directory line
            connector = "└── " if is_last_dir else "├── "
            lines.append(f"{prefix}{connector}{dir_name}/")

            # Recursively process subdirectory
            child_path = f"{path}/{dir_name}" if path else dir_name
            child_prefix = prefix + ("    " if is_last_dir else "│   ")
            child_lines = generate_ascii_tree(
                structure, child_path, child_prefix, is_last_dir
            )
            lines.extend(child_lines)

        # Process files
        for i, (file_name, language) in enumerate(files):
            is_last_file = i == len(files) - 1
            connector = "└── " if is_last_file else "├── "
            lines.append(f"{prefix}{connector}{file_name} ({language})")

        return lines

    # Generate ASCII tree
    structure = build_tree_structure()
    tree_lines = ["# Project Directory Structure", "```", "Project Root/"]
    ascii_lines = generate_ascii_tree(structure)
    tree_lines.extend(ascii_lines)
    tree_lines.append("```")

    # Create Mermaid diagram
    mermaid_lines = ["graph TD"]

    # Map to keep track of node IDs
    node_map = {}
    node_counter = 0

    # Helper function to create node IDs
    def get_node_id(name):
        nonlocal node_counter
        if name not in node_map:
            node_map[name] = f"node{node_counter}"
            node_counter += 1
        return node_map[name]

    # Add root node
    root_id = get_node_id("Project Root")
    mermaid_lines.append(f"    {root_id}[Project Root]")

    # Process directories
    for dir_path in sorted(tree.keys()):
        if dir_path == "root":
            dir_id = root_id
        else:
            # Handle nested directories
            path_parts = dir_path.split("/")
            parent_path = ""
            parent_id = root_id

            for i, part in enumerate(path_parts):
                current_path = (
                    parent_path + part if i == 0 else parent_path + "/" + part
                )
                current_id = get_node_id(current_path)

                if i == len(path_parts) - 1:  # Last part
                    mermaid_lines.append(f"    {current_id}[{part}/]")
                    mermaid_lines.append(f"    {parent_id} --> {current_id}")
                else:  # Intermediate directories
                    if f"    {current_id}[{part}/]" not in mermaid_lines:
                        mermaid_lines.append(f"    {current_id}[{part}/]")
                        mermaid_lines.append(f"    {parent_id} --> {current_id}")

                parent_path = current_path + "/"
                parent_id = current_id

            dir_id = get_node_id(dir_path)

        # Add files for this directory
        for file_name, language in sorted(tree[dir_path]):
            file_id = get_node_id(
                f"{dir_path}/{file_name}" if dir_path != "root" else file_name
            )
            mermaid_lines.append(f'    {file_id}["{file_name}"]')
            mermaid_lines.append(f"    {dir_id} --> {file_id}")

    return tree, "\n".join(tree_lines), "\n".join(mermaid_lines)
