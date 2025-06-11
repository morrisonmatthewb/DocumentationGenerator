"""
Core documentation generation with concurrency support
"""

import time
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import queue
from utils.api import (
    initialize_client,
    generate_documentation,
    generate_project_overview,
    generate_content_based_overview,
)
from utils.archive import extract_files_from_archive
from utils.visualization import build_directory_tree
import os


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
            uploaded_file, config["selected_extensions"], config["max_file_size"]
        )
        return files
    except Exception as e:
        st.error(f"Error extracting archive: {str(e)}")
        st.info(
            "This may be due to missing dependencies. Check the README for installation instructions."
        )
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
        return file_path, documentation, True, ""
    except Exception as e:
        return file_path, f"Error generating documentation: {str(e)}", False, str(e)


def generate_all_documentation_concurrent(files, config, max_workers=3):
    """
    Generate documentation for all files concurrently with Streamlit threading.

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
                        status_container.success(
                            f"Completed: {file_path} ({len(completed_files)}/{total_files})"
                        )
                    else:
                        status_container.error(
                            f"Failed: {file_path} ({len(completed_files)}/{total_files})"
                        )

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
                (file_path, file_info, client, config["doc_level"])
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

    # generate project overview based on actual documentation content
    if config["generate_overview"] and len(files) > 1:
        with st.spinner("Generating content-based project overview..."):
            documentation["__project_overview__"] = generate_content_based_overview(
                documentation, files, client
            )
    # Wait for progress thread to finish
    progress_thread.join(timeout=1.0)

    # Final progress update
    progress_bar.progress(1.0)
    status_container.success(
        f"Documentation generation completed! ({total_files} files processed)"
    )

    # Display generation time
    end_time = time.time()
    processing_time = end_time - start_time
    st.success(f"Documentation generated in {processing_time:.2f} seconds")

    return documentation


def generate_all_documentation_batch(files, config, batch_size=3):
    """
    Batch processing that runs concurrently.

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
        from utils.api import initialize_client

        client = initialize_client(config["api_key"])
    except Exception as e:
        st.error(f"Failed to initialize Claude client: {str(e)}")
        return None

    # Generate directory structure if selected
    if config["generate_dir_structure"] and len(files) > 1:
        with st.spinner("Generating directory structure visualization..."):
            from utils.visualization import build_directory_tree

            tree, ascii_tree, mermaid_code = build_directory_tree(files)

            documentation["__directory_structure__"] = ascii_tree
            documentation["__mermaid_diagram__"] = f"""
# Project Directory Structure (Interactive)

```mermaid
{mermaid_code}
```
"""

    # Process files in batches
    file_items = list(files.items())
    total_files = len(file_items)
    progress_bar = st.progress(0)
    status_placeholder = st.empty()

    completed_count = 0

    for batch_num, i in enumerate(range(0, total_files, batch_size), 1):
        batch = file_items[i : i + batch_size]
        batch_start_time = time.time()

        file_names = [file_path.split("/")[-1] for file_path, _ in batch]
        status_placeholder.info(
            f"📦 Processing Batch {batch_num}: {', '.join(file_names)}"
        )

        # Process current batch concurrently
        batch_results = []

        with ThreadPoolExecutor(max_workers=min(batch_size, len(batch))) as executor:
            future_to_file = {
                executor.submit(
                    generate_file_documentation_worker,
                    (file_path, file_info, client, config["doc_level"]),
                ): file_path
                for file_path, file_info in batch
            }

            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result_file_path, doc, success, error_msg = future.result()

                    if success:
                        documentation[result_file_path] = doc
                        batch_results.append((result_file_path, True))
                    else:
                        documentation[result_file_path] = f"Error: {error_msg}"
                        batch_results.append((result_file_path, False))

                    completed_count += 1

                except Exception as e:
                    error_msg = f"Worker exception: {str(e)}"
                    documentation[file_path] = f"Error: {error_msg}"
                    batch_results.append((file_path, False))
                    completed_count += 1

        # Update progress
        batch_elapsed = time.time() - batch_start_time
        successful = sum(1 for _, success in batch_results if success)

        progress_bar.progress(completed_count / total_files)
        status_placeholder.success(
            f"✅ Batch {batch_num} completed in {batch_elapsed:.2f}s "
            f"({successful}/{len(batch)} files successful)"
        )

    # generate project overview based on actual documentation content
    if config["generate_overview"] and len(files) > 1:
        with st.spinner("Generating content-based project overview..."):
            documentation["__project_overview__"] = generate_content_based_overview(
                documentation, files, client
            )

    # Final progress update
    progress_bar.progress(1.0)

    # Display generation time
    end_time = time.time()
    processing_time = end_time - start_time
    status_placeholder.success(
        f"🎉 Documentation generated in {processing_time:.2f} seconds ({total_files} files)"
    )

    return documentation
