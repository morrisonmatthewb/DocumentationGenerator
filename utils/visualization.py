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

    def generate_mermaid_diagram(structure):
        """Generate Mermaid diagram using the hierarchical structure"""
        mermaid_lines = ["graph TD"]
        
        # Map to keep track of node IDs
        node_map = {}
        node_counter = 0

        def get_node_id(path):
            nonlocal node_counter
            if path not in node_map:
                node_map[path] = f"node{node_counter}"
                node_counter += 1
            return node_map[path]

        def add_mermaid_nodes(structure, current_path=""):
            """Recursively add nodes and connections to Mermaid diagram"""
            current = structure[current_path]
            
            # Get current node ID
            if current_path == "":
                current_id = get_node_id("root")
                mermaid_lines.append(f"    {current_id}[Project Root]")
            else:
                current_id = get_node_id(current_path)
                dir_name = current_path.split("/")[-1]
                mermaid_lines.append(f"    {current_id}[{dir_name}/]")

            # Add subdirectories
            for dir_name in sorted(current["dirs"]):
                child_path = f"{current_path}/{dir_name}" if current_path else dir_name
                child_id = get_node_id(child_path)
                
                # Add connection from current to child
                mermaid_lines.append(f"    {current_id} --> {child_id}")
                
                # Recursively process child directory
                add_mermaid_nodes(structure, child_path)

            # Add files
            for file_name, language in sorted(current["files"]):
                file_path = f"{current_path}/{file_name}" if current_path else file_name
                file_id = get_node_id(file_path)
                mermaid_lines.append(f'    {file_id}["{file_name}"]')
                mermaid_lines.append(f"    {current_id} --> {file_id}")

        # Generate the diagram
        add_mermaid_nodes(structure)
        return "\n".join(mermaid_lines)

    # Generate ASCII tree
    structure = build_tree_structure()
    tree_lines = ["# Project Directory Structure", "```", "Project Root/"]
    ascii_lines = generate_ascii_tree(structure)
    tree_lines.extend(ascii_lines)
    tree_lines.append("```")
    
    mermaid_diagram = generate_mermaid_diagram(structure)

    return tree, "\n".join(tree_lines), mermaid_diagram