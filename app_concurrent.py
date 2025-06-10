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
    display_file_summary,
    display_file_summary_enhanced,
    display_documentation,
    display_download_options,
)
from core.concurrent_docgen import (
    process_archive,
    generate_all_documentation_concurrent_fixed,
    generate_all_documentation_batch,
)
from utils.demo import (
    check_demo_operation,
    update_demo_usage,
    apply_demo_config_restrictions,
)
from utils.api import (simple_get_api_key)
from utils.debug import show_debug_info
# Load environment variables at the application start
load_dotenv(dotenv_path=".env", verbose=True)


def main():
    """Main application function with history integration."""
    # Setup page
    setup_page()

    # Display title and description
    st.title("Documentation Generator")
    st.write("Upload archive files to generate documentation with improved performance")

    # Add documentation history in sidebar
    display_documentation_history_sidebar()


    # Get configuration and apply demo restrictions
    config = sidebar_config()
    # config = apply_demo_config_restrictions(config)

    # Add main tab layout
    tab1, tab2 = st.tabs(["📝 Generate Documentation", "📚 Documentation History"])

    with tab1:
        if not config["api_key"]:
            st.warning("Please enter your Anthropic API key to continue")
            return

        # Display file uploader
        uploaded_file, file_extension, archive_format = file_uploader_section()

        if uploaded_file is not None:
            # file_size = uploaded_file.size
            # if not check_demo_operation("upload", file_size=file_size):  # NEW: Check limits
                # return
            # Processing indicators
            with st.spinner(f"Processing {archive_format} archive..."):
                files = process_archive(uploaded_file, file_extension, config)
                if files:
                    # Update demo usage
                    # update_demo_usage('upload')

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
                # Check demo limits before documentation generation
                # total_size = sum(len(info['content'].encode()) for info in files.values())
                # if not check_demo_operation('process', file_count=len(files), total_size=total_size):
                    #return
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
                        documentation = generate_all_documentation_concurrent_fixed(
                            files, config, config.get("max_workers", 3)
                        )
                    else:
                        from core.docgen import generate_all_documentation

                        st.info("Using sequential processing")
                        documentation = generate_all_documentation(files, config)

                    if documentation:
                        # Update demo usage after successful processing
                        # update_demo_usage('process', file_count=len(files), total_size=total_size)
                        
                        # Store in session state
                        st.session_state.documentation = documentation

                        save_current_documentation(documentation, uploaded_file.name)

                        # Display results
                        display_documentation(documentation)
                        display_download_options(documentation, "_current")
                    else:
                        st.error("Documentation generation failed.")
                        return

        # If documentation was previously generated, show it from session state
        elif "documentation" in st.session_state:
            documentation = st.session_state.documentation
            display_documentation(documentation)
            display_download_options(documentation, "_cached")

    with tab2:
        display_documentation_history()
    if os.getenv("DEBUG") == "true":
        show_debug_info()


if __name__ == "__main__":
    main()
