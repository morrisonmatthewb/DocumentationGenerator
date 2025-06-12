"""
Automatic Documentation Generator - Concurrent Version
"""

import streamlit as st
import os
from dotenv import load_dotenv
from utils.documentation_history import (
    display_documentation_history,
    display_documentation_history_sidebar,
    save_current_documentation,
)
from utils.ui import (
    setup_page,
    sidebar_config,
    file_uploader_section,
    display_file_summary_enhanced,
    display_documentation,
    display_download_options,
)
from core.concurrent_docgen import (
    process_archive,
    generate_all_documentation_concurrent,
    generate_all_documentation_batch,
)
from utils.debug import show_debug_info


load_dotenv(dotenv_path=".env", verbose=True)

def main():
    """Main application function with history integration."""
    # Setup page
    setup_page()
    demo_pw = os.getenv("DEMO_PW")

    # Display title and description
    st.title("Documentation Generator")
    st.write("Upload archive files to generate documentation using AI.")

    # Add documentation history in sidebar
    display_documentation_history_sidebar()

    # Get configuration and apply demo restrictions
    config = sidebar_config()
    st.session_state.force_content_overview = False if st.session_state.anthropic_api_key and st.session_state.anthropic_api_key == demo_pw else config.get("force_content_overview")

    # Add main tab layout
    tab1, tab2 = st.tabs(["📝 Generate Documentation", "📚 Documentation History"])

    with tab1:
        if not config["api_key"]:
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
            files_valid = display_file_summary_enhanced(files)
            if not files_valid:
                return

            # Generate documentation button
            if st.button("Generate Documentation", key="generate_docs_button"):
                with st.container():
                    st.subheader("Documentation Generation Progress")

                    # Choose the appropriate generation method
                    if config.get("concurrency_method") == "Batch Processing":
                        st.info(
                            f"Using batch processing with batch size: {config.get('batch_size', 3)}"
                        )
                        documentation = generate_all_documentation_batch(
                            files, config, config.get("batch_size", 3)
                        )
                    elif config.get("concurrency_method") == "Full Concurrent":
                        st.info(
                            f"Using concurrent processing with {config.get('max_workers', 3)} workers"
                        )
                        documentation = generate_all_documentation_concurrent(
                            files, config, config.get("max_workers", 3)
                        )
                    else:
                        from core.docgen import generate_all_documentation

                        st.info("Using sequential processing")
                        documentation = generate_all_documentation(files, config)

                    if documentation:
                        
                        # Store in session state
                        st.session_state.documentation = documentation

                        save_current_documentation(documentation, uploaded_file.name)

                        # Display results
                        display_documentation(documentation)
                        display_download_options(documentation, "_current", uploaded_file.name)
                    else:
                        st.error("Documentation generation failed.")
                        return

        # If documentation was previously generated, show it from session state
        elif "documentation" in st.session_state:
            documentation = st.session_state.documentation
            display_documentation(documentation)
            display_download_options(documentation, "_cached", uploaded_file.name)

    with tab2:
        display_documentation_history()
    if os.getenv("DEBUG"):
        show_debug_info()


if __name__ == "__main__":
    main()
