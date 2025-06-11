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
        dir_path = file_info.get('directory', '')
        file_name = os.path.basename(file_path)
        
        if dir_path:
            tree[dir_path].append((file_name, file_info['language']))
        else:
            tree['root'].append((file_name, file_info['language']))
    
    # Generate directory structure in ASCII art
    tree_ascii = ["# Project Directory Structure", "```", "Project Root"]
    
    # First process directories
    sorted_dirs = sorted([d for d in tree.keys() if d != 'root'])
    
    # Helper function to get directory depth
    def get_depth(path):
        if not path:
            return 0
        return path.count('/') + 1
    
    # Add directories with proper indentation
    for dir_path in sorted_dirs:
        depth = get_depth(dir_path)
        parts = dir_path.split('/')
        dir_name = parts[-1]
        tree_ascii.append("│" + "   │" * (depth - 1) + "───" + dir_name)
    
    # Add files in root with proper indentation
    if 'root' in tree:
        for file_name, language in sorted(tree['root']):
            tree_ascii.append("│───" + file_name + f" ({language})")
    
    # Add files in each directory with proper indentation
    for dir_path in sorted_dirs:
        depth = get_depth(dir_path)
        for file_name, language in sorted(tree[dir_path]):
            tree_ascii.append("│" + "   │" * depth + "─── " + file_name + f" ({language})")
    
    tree_ascii.append("```")
    
    # Also create a Mermaid diagram as an alternative visualization
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
        if dir_path == 'root':
            dir_id = root_id
        else:
            # Handle nested directories
            path_parts = dir_path.split('/')
            parent_path = ''
            parent_id = root_id
            
            for i, part in enumerate(path_parts):
                current_path = parent_path + part if i == 0 else parent_path + '/' + part
                current_id = get_node_id(current_path)
                
                if i == len(path_parts) - 1:  # Last part
                    mermaid_lines.append(f"    {current_id}[{part}/]")
                    mermaid_lines.append(f"    {parent_id} --> {current_id}")
                else:  # Intermediate directories
                    if f"    {current_id}[{part}/]" not in mermaid_lines:
                        mermaid_lines.append(f"    {current_id}[{part}/]")
                        mermaid_lines.append(f"    {parent_id} --> {current_id}")
                
                parent_path = current_path + '/'
                parent_id = current_id
            
            dir_id = get_node_id(dir_path)
    
        # Add files for this directory
        for file_name, language in sorted(tree[dir_path]):
            file_id = get_node_id(f"{dir_path}/{file_name}" if dir_path != 'root' else file_name)
            mermaid_lines.append(f"    {file_id}[\"{file_name}\"]")
            mermaid_lines.append(f"    {dir_id} --> {file_id}")
    
    return tree, "\n".join(tree_ascii), "\n".join(mermaid_lines)