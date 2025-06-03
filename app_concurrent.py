"""
Automatic Documentation Generator - Concurrent Version

This version fixes the ScriptRunContext threading issues with Streamlit.
"""

import streamlit as st
import os
from dotenv import load_dotenv

# Import from utils
from utils.ui import (
    setup_page,
    sidebar_config,
    file_uploader_section,
    display_file_summary,
    display_documentation,
    display_download_options
)

# Import from core - using the fixed concurrent implementation
from core.concurrent_docgen import (
    process_archive, 
    generate_all_documentation_concurrent_fixed,
    generate_all_documentation_batch
)

# Load environment variables at the application start
load_dotenv(dotenv_path='.env', verbose=True)

def main():
    """Main application function."""
    # Setup page
    setup_page()
    
    # Display title and description
    st.title("🤖 Advanced Documentation Generator (Concurrent)")
    st.write("Upload archive files to generate documentation with improved performance")
    
    # Get configuration from sidebar
    config = sidebar_config()
    
    # Add concurrency options
    st.sidebar.subheader("Performance Settings")
    concurrency_method = st.sidebar.radio(
        "Processing Method:",
        ["Sequential", "Batch Processing", "Full Concurrent"],
        index=1,  # Default to Batch Processing (more stable)
        help="Choose how to process multiple files"
    )
    
    if concurrency_method != "Sequential":
        if concurrency_method == "Batch Processing":
            batch_size = st.sidebar.slider(
                "Batch Size",
                min_value=2,
                max_value=5,
                value=3,
                help="Number of files to process simultaneously in each batch"
            )
        else:
            max_workers = st.sidebar.slider(
                "Max Workers",
                min_value=2,
                max_value=8,
                value=3,
                help="Maximum number of concurrent threads (keep low to avoid API issues)"
            )
    
    if not config['api_key']:
        st.warning("Please enter your Anthropic API key to continue")
        return
    
    # Display file uploader
    uploaded_file, file_extension, archive_format = file_uploader_section()
    
    if uploaded_file is not None:
        # Processing indicators
        with st.spinner(f"Processing {archive_format} archive..."):
            files = process_archive(uploaded_file, file_extension, config)
            if files:
                st.success(f"Successfully extracted {archive_format} archive")
            else:
                return
        
        # Store session state
        if "files" not in st.session_state:
            st.session_state.files = files
        
        # Display file summary
        files_valid = display_file_summary(files)
        if not files_valid:
            return
        
        # Generate documentation button
        if st.button("Generate Documentation", key="generate_docs_button"):
            with st.container():
                st.subheader("Documentation Generation Progress")
                
                # Choose the appropriate generation method
                if concurrency_method == "Batch Processing":
                    st.info(f"Using batch processing with batch size: {batch_size}")
                    documentation = generate_all_documentation_batch(files, config, batch_size)
                elif concurrency_method == "Full Concurrent":
                    st.info(f"Using concurrent processing with {max_workers} workers")
                    documentation = generate_all_documentation_concurrent_fixed(files, config, max_workers)
                else:
                    # Use the original sequential method
                    from core.docgen import generate_all_documentation
                    st.info("Using sequential processing")
                    documentation = generate_all_documentation(files, config)
                
                if documentation:
                    # Store in session state
                    st.session_state.documentation = documentation
                else:
                    st.error("Documentation generation failed.")
                    return
            
            # Display results
            display_documentation(documentation)
            
            # Display download options
            display_download_options(documentation, "_top")
    
    # If documentation was previously generated but we're not in the generation flow,
    # show it from session state
    elif "documentation" in st.session_state:
        documentation = st.session_state.documentation
        
        display_documentation(documentation)
        display_download_options(documentation, "_bottom")


if __name__ == "__main__":
    main()