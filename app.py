"""
Automatic Documentation Generator - Main Application

This web application takes archive files containing code files, extracts them,
and automatically generates documentation using the Claude API.
"""

import streamlit as st
import os
from dotenv import load_dotenv

# Import from utils - directly import specific functions to avoid circular imports
from utils.ui import (
    setup_page,
    sidebar_config,
    file_uploader_section,
    display_file_summary,
    display_documentation,
    display_download_options
)

# Import from core
from core.docgen import process_archive, generate_all_documentation

# Load environment variables at the application start
load_dotenv(dotenv_path='.env', verbose=True)

# Debug: Print environment variables (remove in production)
if os.getenv('ANTHROPIC_API_KEY'):
    print("API key found in environment variables")
else:
    print("API key not found in environment variables")

def main():
    """Main application function."""
    # Setup page
    setup_page()
    
    # Display title and description
    st.title("🤖 Advanced Documentation Generator")
    st.write("Upload archive files to generate documentation")
    
    # Get configuration from sidebar
    config = sidebar_config()
    
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
            with st.spinner("Generating documentation..."):
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