"""
Core documentation generation with concurrency support.
"""

import time
import asyncio
import streamlit as st
from typing import Dict, Any, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils.api import initialize_client, generate_documentation, generate_project_overview
from utils.archive import extract_files_from_archive
from utils.visualization import build_directory_tree
from utils.ui import display_documentation_progress, display_generation_time


def process_archive(uploaded_file, file_extension, config):
    """
    Extract files from the uploaded archive based on configuration.
    
    Args:
        uploaded_file: The uploaded archive file
        file_extension: The file extension of the archive
        config: Configuration dictionary
        
    Returns:
        Dictionary of extracted files or None if error
    """
    try:
        files = extract_files_from_archive(
            uploaded_file, 
            config['selected_extensions'], 
            config['max_file_size']
        )
        return files
    except Exception as e:
        st.error(f"Error extracting archive: {str(e)}")
        st.info("This may be due to missing dependencies. Check the README for installation instructions.")
        return None


def generate_file_documentation(args):
    """
    Generate documentation for a single file (used for parallel processing).
    
    Args:
        args: Tuple of (file_path, file_info, client, doc_level, progress_callback)
        
    Returns:
        Tuple of (file_path, documentation)
    """
    file_path, file_info, client, doc_level, idx, total = args
    documentation = generate_documentation(file_path, file_info, client, doc_level)
    
    # Update progress in the main thread if callback provided
    if st.session_state.get('progress_placeholder'):
        progress = (idx + 1) / total
        st.session_state['progress_values'][file_path] = progress
    
    return file_path, documentation


def generate_all_documentation_concurrent(files, config, max_workers=5):
    """
    Generate documentation for all files concurrently.
    
    Args:
        files: Dictionary of extracted files
        config: Configuration dictionary
        max_workers: Maximum number of concurrent worker threads
        
    Returns:
        Dictionary containing all generated documentation
    """
    documentation = {}
    start_time = time.time()
    
    # Initialize client
    try:
        client = initialize_client(config['api_key'])
    except Exception as e:
        st.error(f"Failed to initialize Claude client: {str(e)}")
        return None
    
    # Setup progress tracking
    total_files = len(files)
    st.session_state['progress_values'] = {}
    progress_placeholder = st.empty()
    st.session_state['progress_placeholder'] = progress_placeholder
    
    # Create progress bar
    progress_bar = progress_placeholder.progress(0)
    
    # Generate directory structure visualization if selected
    if config['generate_dir_structure'] and len(files) > 1:
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
    
    # Generate project overview if selected
    if config['generate_overview'] and len(files) > 1:
        with st.spinner("Generating project overview..."):
            documentation["__project_overview__"] = generate_project_overview(files, client)
    
    # Function to update progress bar
    def update_progress():
        while not st.session_state.get('generation_complete', False):
            if st.session_state.get('progress_values'):
                progress = sum(st.session_state['progress_values'].values()) / total_files
                progress_bar.progress(progress)
            time.sleep(0.1)
    
    # Start progress updater in a separate thread
    import threading
    progress_thread = threading.Thread(target=update_progress)
    progress_thread.daemon = True
    progress_thread.start()
    
    try:
        # Process each file concurrently
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Prepare the arguments for each file
            file_args = [
                (file_path, file_info, client, config['doc_level'], idx, total_files)
                for idx, (file_path, file_info) in enumerate(files.items())
            ]
            
            # Submit all tasks
            future_to_file = {
                executor.submit(generate_file_documentation, args): args[0]
                for args in file_args
            }
            
            # Process results as they complete
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    file_path, doc = future.result()
                    documentation[file_path] = doc
                    
                    # Update status message
                    st.write(f"Completed documentation for: {file_path}")
                except Exception as e:
                    st.error(f"Error processing {file_path}: {str(e)}")
                    documentation[file_path] = f"Error generating documentation: {str(e)}"
    finally:
        # Mark generation as complete
        st.session_state['generation_complete'] = True
        
        # Ensure progress bar shows 100%
        progress_bar.progress(1.0)
    
    # Display generation time
    display_generation_time(start_time)
    
    return documentation


# Async version if you prefer using asyncio instead of ThreadPoolExecutor
async def generate_all_documentation_async(files, config, max_concurrent=5):
    """
    Generate documentation for all files using asyncio.
    
    Args:
        files: Dictionary of extracted files
        config: Configuration dictionary
        max_concurrent: Maximum number of concurrent API calls
        
    Returns:
        Dictionary containing all generated documentation
    """
    documentation = {}
    start_time = time.time()
    
    # Initialize client
    try:
        client = initialize_client(config['api_key'])
    except Exception as e:
        st.error(f"Failed to initialize Claude client: {str(e)}")
        return None
    
    # Generate directory structure visualization if selected
    if config['generate_dir_structure'] and len(files) > 1:
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
    
    # Generate project overview if selected
    if config['generate_overview'] and len(files) > 1:
        with st.spinner("Generating project overview..."):
            documentation["__project_overview__"] = generate_project_overview(files, client)
    
    # Setup progress tracking
    total_files = len(files)
    progress_bar = st.progress(0)
    completed = 0
    
    # Create a semaphore to limit concurrent API calls
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_file(file_path, file_info):
        async with semaphore:
            # Run the API call in a thread to avoid blocking the event loop
            doc = await asyncio.to_thread(
                generate_documentation, 
                file_path, 
                file_info, 
                client, 
                config['doc_level']
            )
            
            nonlocal completed
            completed += 1
            progress_bar.progress(completed / total_files)
            st.write(f"Completed documentation for: {file_path}")
            
            return file_path, doc
    
    # Create tasks for all files
    tasks = [
        process_file(file_path, file_info)
        for file_path, file_info in files.items()
    ]
    
    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks)
    
    # Process results
    for file_path, doc in results:
        documentation[file_path] = doc
    
    # Display generation time
    display_generation_time(start_time)
    
    return documentation