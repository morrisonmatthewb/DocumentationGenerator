"""
Core documentation generation with concurrency support
"""

import time
import asyncio
import streamlit as st
from typing import Dict, Any, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import queue
from utils.api import initialize_client, generate_documentation, generate_project_overview
from utils.archive import extract_files_from_archive
from utils.visualization import build_directory_tree


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


def generate_file_documentation_worker(args):
    """
    Generate documentation for a single file (worker function for threading).
    This function runs in a background thread without Streamlit context.
    
    Args:
        args: Tuple of (file_path, file_info, client, doc_level)
        
    Returns:
        Tuple of (file_path, documentation, success)
    """
    file_path, file_info, client, doc_level = args
    
    try:
        documentation = generate_documentation(file_path, file_info, client, doc_level)
        return file_path, documentation, True
    except Exception as e:
        return file_path, f"Error generating documentation: {str(e)}", False


def generate_all_documentation_concurrent_fixed(files, config, max_workers=3):
    """
    Generate documentation for all files concurrently with proper Streamlit threading.
    
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
    status_container = st.empty()
    
    # Create a queue for progress updates
    progress_queue = queue.Queue()
    completed_files = []
    
    # Function to update progress from main thread
    def update_progress_display():
        while len(completed_files) < total_files:
            try:
                # Non-blocking check for progress updates
                while not progress_queue.empty():
                    file_path, success = progress_queue.get_nowait()
                    completed_files.append(file_path)
                    
                    # Update progress bar
                    progress = len(completed_files) / total_files
                    progress_bar.progress(progress)
                    
                    # Update status
                    if success:
                        status_container.success(f"Completed: {file_path} ({len(completed_files)}/{total_files})")
                    else:
                        status_container.error(f"Failed: {file_path} ({len(completed_files)}/{total_files})")
                
                # Small delay to prevent busy waiting
                time.sleep(0.1)
                
            except queue.Empty:
                time.sleep(0.1)
                continue
    
    # Start progress updater in a separate thread
    progress_thread = threading.Thread(target=update_progress_display, daemon=True)
    progress_thread.start()
    
    try:
        # Process files concurrently
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Prepare arguments for each file
            file_args = [
                (file_path, file_info, client, config['doc_level'])
                for file_path, file_info in files.items()
            ]
            
            # Submit all tasks
            future_to_file = {
                executor.submit(generate_file_documentation_worker, args): args[0]
                for args in file_args
            }
            
            # Process results as they complete
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result_file_path, doc, success = future.result()
                    documentation[result_file_path] = doc
                    
                    # Signal progress update through queue
                    progress_queue.put((result_file_path, success))
                    
                except Exception as e:
                    error_msg = f"Error processing {file_path}: {str(e)}"
                    documentation[file_path] = error_msg
                    progress_queue.put((file_path, False))
    
    except Exception as e:
        st.error(f"Error in concurrent processing: {str(e)}")
        return None
    
    # Wait for progress thread to finish
    progress_thread.join(timeout=1.0)
    
    # Final progress update
    progress_bar.progress(1.0)
    status_container.success(f"Documentation generation completed! ({total_files} files processed)")
    
    # Display generation time
    end_time = time.time()
    processing_time = end_time - start_time
    st.success(f"Documentation generated in {processing_time:.2f} seconds")
    
    return documentation


def generate_all_documentation_batch(files, config, batch_size=3):
    """
    Generate documentation in batches to reduce threading complexity.
    This is a simpler alternative that processes files in small batches.
    
    Args:
        files: Dictionary of extracted files
        config: Configuration dictionary
        batch_size: Number of files to process in each batch
        
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
            
            documentation["__directory_structure__"] = ascii_tree
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
    
    # Process files in batches
    file_items = list(files.items())
    total_files = len(file_items)
    progress_bar = st.progress(0)
    
    for i in range(0, total_files, batch_size):
        batch = file_items[i:i + batch_size]
        
        # Process current batch concurrently
        with ThreadPoolExecutor(max_workers=min(batch_size, len(batch))) as executor:
            # Submit batch tasks
            batch_futures = {
                executor.submit(
                    generate_file_documentation_worker,
                    (file_path, file_info, client, config['doc_level'])
                ): file_path
                for file_path, file_info in batch
            }
            
            # Process batch results
            for future in as_completed(batch_futures):
                file_path = batch_futures[future]
                try:
                    result_file_path, doc, success = future.result()
                    documentation[result_file_path] = doc
                    
                    # Update progress
                    completed = len([k for k in documentation.keys() 
                                   if not k.startswith('__')])
                    progress_bar.progress(completed / total_files)
                    st.write(f"Completed: {result_file_path}")
                    
                except Exception as e:
                    st.error(f"Error processing {file_path}: {str(e)}")
                    documentation[file_path] = f"Error: {str(e)}"
    
    # Final progress update
    progress_bar.progress(1.0)
    
    # Display generation time
    end_time = time.time()
    processing_time = end_time - start_time
    st.success(f"Documentation generated in {processing_time:.2f} seconds")
    
    return documentation