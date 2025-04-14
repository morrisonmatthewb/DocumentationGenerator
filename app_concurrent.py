"""
Automatic Documentation Generator - Main Application with Concurrent Processing

This web application takes archive files containing code files, extracts them,
and automatically generates documentation using the Claude API with concurrent processing.
"""

import streamlit as st
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables at the application start
load_dotenv(dotenv_path='.env', verbose=True)

# Import from utils - directly import specific functions to avoid circular imports
from utils.ui import (
    setup_page,
    sidebar_config,
    file_uploader_section,
    display_file_summary,
    display_documentation,
    display_download_options
)

# Import from core - using the concurrent implementation
from core.concurrent_docgen import (
    process_archive, 
    generate_all_documentation_concurrent,
    generate_all_documentation_async
)


def main():
    """Main application function."""
    # Setup page
    setup_page()
    
    # Display title and description
    st.title("🤖 Advanced Documentation Generator")
    st.write("Upload archive files to generate documentation")
    
    # Get configuration from sidebar
    config = sidebar_config()
    
    # Add concurrency options
    st.sidebar.subheader("Performance Settings")
    concurrency_method = st.sidebar.radio(
        "Concurrency Method:",
        ["Sequential", "ThreadPool", "Asyncio"],
        index=1,  # Default to ThreadPool
        help="Choose how to parallelize documentation generation"
    )
    
    if concurrency_method != "Sequential":
        max_workers = st.sidebar.slider(
            "Max Concurrent Requests",
            min_value=2,
            max_value=10,
            value=5,
            help="Maximum number of concurrent API calls to Claude"
        )
    else:
        max_workers = 1
    
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
        
        # Initialize session state for generation
        if 'generation_complete' in st.session_state:
            del st.session_state['generation_complete']
        
        # Generate documentation button
        if st.button("Generate Documentation", key="generate_docs_button"):
            with st.spinner("Generating documentation..."):
                # Choose the appropriate generation method
                if concurrency_method == "ThreadPool":
                    st.info(f"Using ThreadPool with {max_workers} workers for concurrent generation")
                    documentation = generate_all_documentation_concurrent(files, config, max_workers)
                elif concurrency_method == "Asyncio":
                    st.info(f"Using Asyncio with {max_workers} concurrent tasks")
                    # For asyncio, we need to run the async function
                    async def run_async():
                        return await generate_all_documentation_async(files, config, max_workers)
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    documentation = loop.run_until_complete(run_async())
                    loop.close()
                else:
                    # Use the original sequential method from core.docgen
                    from core.docgen import generate_all_documentation
                    st.info("Using sequential generation (no concurrency)")
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