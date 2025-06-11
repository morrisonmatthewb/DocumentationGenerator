"""
Documentation History Manager - Stores and manages previously generated documentation.
Provides functionality to list and download previous documentation generations.
"""

import streamlit as st
import json
import datetime
from typing import Dict, List, Any, Optional
import hashlib
from utils.documentation import build_combined_documentation
from utils.html import convert_markdown_to_html


class DocumentationHistory:
    """Manages the history of generated documentation in session state."""

    @staticmethod
    def initialize_history():
        """Initialize the documentation history in session state if it doesn't exist."""
        if "documentation_history" not in st.session_state:
            st.session_state.documentation_history = []

    @staticmethod
    def add_documentation(
        documentation: Dict[str, str], project_name: str = None
    ) -> str:
        """
        Add a new documentation entry to the history.

        Args:
            documentation: Dictionary containing the generated documentation
            project_name: Optional name for the project (extracted from archive filename)

        Returns:
            Unique ID for the documentation entry
        """
        DocumentationHistory.initialize_history()

        # Generate unique ID based on content and timestamp
        timestamp = datetime.datetime.now()
        content_hash = hashlib.md5(
            json.dumps(documentation, sort_keys=True).encode()
        ).hexdigest()[:8]
        doc_id = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{content_hash}"

        # Count files and get file types
        file_count = len([k for k in documentation.keys() if not k.startswith("__")])
        file_types = set()
        for key in documentation.keys():
            if not key.startswith("__"):
                # Extract file extension for type counting
                if "." in key:
                    ext = key.split(".")[-1].lower()
                    file_types.add(ext)

        # Create entry
        entry = {
            "id": doc_id,
            "timestamp": timestamp.isoformat(),
            "display_time": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "project_name": project_name or f"Project_{timestamp.strftime('%H%M%S')}",
            "documentation": documentation,
            "file_count": file_count,
            "file_types": list(file_types),
            "has_overview": "__project_overview__" in documentation,
            "has_structure": "__directory_structure__" in documentation,
            "size_estimate": len(json.dumps(documentation)) // 1024,  # KB estimate
        }

        # Add to beginning of history (most recent first)
        st.session_state.documentation_history.insert(0, entry)

        # Keep only last 10 entries to avoid memory issues
        if len(st.session_state.documentation_history) > 10:
            st.session_state.documentation_history = (
                st.session_state.documentation_history[:10]
            )

        return doc_id

    @staticmethod
    def get_history() -> List[Dict[str, Any]]:
        """Get the complete documentation history."""
        DocumentationHistory.initialize_history()
        return st.session_state.documentation_history

    @staticmethod
    def get_documentation_by_id(doc_id: str) -> Optional[Dict[str, str]]:
        """Get documentation by its unique ID."""
        history = DocumentationHistory.get_history()
        for entry in history:
            if entry["id"] == doc_id:
                return entry["documentation"]
        return None

    @staticmethod
    def remove_documentation(doc_id: str) -> bool:
        """Remove documentation from history by ID."""
        DocumentationHistory.initialize_history()
        original_count = len(st.session_state.documentation_history)
        st.session_state.documentation_history = [
            entry
            for entry in st.session_state.documentation_history
            if entry["id"] != doc_id
        ]
        return len(st.session_state.documentation_history) < original_count

    @staticmethod
    def clear_history():
        """Clear all documentation history."""
        st.session_state.documentation_history = []


def display_documentation_history():
    """Display the documentation history interface."""
    DocumentationHistory.initialize_history()
    history = DocumentationHistory.get_history()

    if not history:
        st.info(
            "No previous documentation found. Generate some documentation to see it listed here!"
        )
        return

    st.subheader(f"📚 Documentation History ({len(history)} generations)")

    # Clear history button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🗑️ Clear History", help="Remove all previous documentation"):
            DocumentationHistory.clear_history()
            st.success("History cleared!")
            st.rerun()

    # Display each entry
    for entry in history:
        with st.expander(
            f"📄 {entry['project_name']} - {entry['display_time']} "
            f"({entry['file_count']} files, {entry['size_estimate']}KB)",
            expanded=False,
        ):
            # Entry details
            col1, col2 = st.columns([2, 1])

            with col1:
                st.write(f"**Generated:** {entry['display_time']}")
                st.write(f"**Files:** {entry['file_count']}")
                if entry["file_types"]:
                    st.write(f"**File Types:** {', '.join(entry['file_types'])}")

                features = []
                if entry["has_overview"]:
                    features.append("Project Overview")
                if entry["has_structure"]:
                    features.append("Directory Structure")
                if features:
                    st.write(f"**Includes:** {', '.join(features)}")

                st.write(f"**Size:** ~{entry['size_estimate']} KB")

            with col2:
                # Action buttons
                st.write("**Actions:**")

                # Download buttons
                documentation = entry["documentation"]
                combined_docs = build_combined_documentation(documentation)

                # Markdown download
                st.download_button(
                    label="📥 Markdown",
                    data=combined_docs,
                    file_name=f"{entry['project_name']}_docs.md",
                    mime="text/markdown",
                    key=f"download_md_{entry['id']}_side",
                )

                # JSON download
                json_data = json.dumps(documentation, indent=2)
                st.download_button(
                    label="📥 JSON",
                    data=json_data,
                    file_name=f"{entry['project_name']}_docs.json",
                    mime="application/json",
                    key=f"download_json_{entry['id']}_side",
                )

                # HTML download
                try:
                    html_content = convert_markdown_to_html(
                        combined_docs, title=f"{entry['project_name']} Documentation"
                    )
                    st.download_button(
                        label="📥 HTML",
                        data=html_content,
                        file_name=f"{entry['project_name']}_docs.html",
                        mime="text/html",
                        key=f"download_html_{entry['id']}_side",
                    )
                except Exception as e:
                    st.error(f"Error generating HTML: {str(e)}")

                # Remove button
                if st.button("🗑️ Remove", key=f"remove_{entry['id']}"):
                    if DocumentationHistory.remove_documentation(entry["id"]):
                        st.success("Documentation removed!")
                        st.rerun()


def display_documentation_history_sidebar():
    """Display a compact version of documentation history in the sidebar."""
    DocumentationHistory.initialize_history()
    history = DocumentationHistory.get_history()

    if not history:
        return

    st.sidebar.subheader(f"📚 Recent Docs ({len(history)})")

    for entry in history[:3]:  # Show only the 3 most recent
        with st.sidebar.expander(f"{entry['project_name'][:20]}...", expanded=False):
            st.write(f"⏰ {entry['display_time']}")
            st.write(f"📁 {entry['file_count']} files")

            # Quick download buttons
            documentation = entry["documentation"]
            combined_docs = build_combined_documentation(documentation)
            
            # MD download
            st.download_button(
                label="📥 MD",
                data=combined_docs,
                file_name=f"{entry['project_name']}_docs.md",
                mime="text/markdown",
                key=f"sidebar_md_{entry['id']}",
            )
            # JSON download
            json_data = json.dumps(documentation, indent=2)
            st.download_button(
                label="📥 JSON",
                data=json_data,
                file_name=f"{entry['project_name']}_docs.json",
                mime="application/json",
                key=f"download_json_{entry['id']}",
            )

            # HTML download
            try:
                html_content = convert_markdown_to_html(
                    combined_docs, title=f"{entry['project_name']} Documentation"
                )
                st.download_button(
                    label="📥 HTML",
                    data=html_content,
                    file_name=f"{entry['project_name']}_docs.html",
                    mime="text/html",
                    key=f"download_html_{entry['id']}",
                )
            except Exception as e:
                st.error(f"Error generating HTML: {str(e)}")

    if len(history) > 3:
        st.sidebar.write(f"... and {len(history) - 3} more in main history")
    st.sidebar.markdown("---")


def save_current_documentation(
    documentation: Dict[str, str], archive_filename: str = None
):
    """
    Save the current documentation to history.
    Call this after successful documentation generation.

    Args:
        documentation: The generated documentation
        archive_filename: Original archive filename for project name
    """
    project_name = None
    if archive_filename:
        # Extract project name from filename
        project_name = (
            archive_filename.split(".")[0]
            if "." in archive_filename
            else archive_filename
        )

    doc_id = DocumentationHistory.add_documentation(documentation, project_name)
    st.success(f"Documentation saved to history! (ID: {doc_id[:8]}...)")
    return doc_id
