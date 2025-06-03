"""
Demo mode implementation with usage limits.
Add these functions to utils/demo.py and integrate with your existing code.
"""

import streamlit as st
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import json
import hashlib
import os

# Demo configuration
DEMO_CONFIG = {
    "trigger_words": ["demo"],
    "demo_api_key": os.getenv("DEMO_KEY"),
    "daily_limits": {
        "max_files": 20,  # Max files per day
        "max_archives": 3,  # Max archives per day
        "max_file_size_mb": 20,  # Smaller file size limit
        "max_total_size_mb": 60,  # Max total content per day
    },
    "session_limits": {
        "max_files": 20,  # Max files per session
        "max_archives": 3,  # Max archives per session
    },
    "feature_restrictions": {
        "doc_level": "comprehensive",  # Force basic documentation level
        "concurrent_mode": False,  # Disable concurrent processing
        "history_limit": 2,  # Limit history entries
        "export_formats": ["markdown"],  # Only allow markdown export
    },
}


class DemoManager:
    """Manages demo mode functionality and limits."""

    def __init__(self):
        self.init_demo_tracking()

    def init_demo_tracking(self):
        """Initialize demo usage tracking in session state."""
        if "demo_usage" not in st.session_state:
            st.session_state.demo_usage = {
                "is_demo_mode": False,
                "session_start": time.time(),
                "session_files": 0,
                "session_archives": 0,
                "session_size": 0,
                "daily_key": self.get_daily_key(),
                "daily_files": 0,
                "daily_archives": 0,
                "daily_size": 0,
                "first_demo_use": datetime.now().isoformat(),
            }

        # Reset daily counters if it's a new day
        current_daily_key = self.get_daily_key()
        if st.session_state.demo_usage["daily_key"] != current_daily_key:
            st.session_state.demo_usage.update(
                {
                    "daily_key": current_daily_key,
                    "daily_files": 0,
                    "daily_archives": 0,
                    "daily_size": 0,
                }
            )

    def get_daily_key(self) -> str:
        """Generate a key for daily usage tracking."""
        return datetime.now().strftime("%Y-%m-%d")

    def is_demo_trigger(self, api_key: str) -> bool:
        """Check if the API key is a demo trigger word."""
        if not api_key:
            return False
        return api_key.lower().strip() in DEMO_CONFIG["trigger_words"]

    def activate_demo_mode(self, api_key_input: str) -> str:
        """Activate demo mode and return the actual demo API key."""
        st.session_state.demo_usage["is_demo_mode"] = True

        # Show demo mode activation message
        st.info(f"""
        🎭 **Demo Mode Activated!**
        
        You've entered "{api_key_input}" which activates our demo mode. 
        This lets you try the documentation generator with some limitations:
        
        **Daily Limits:**
        - 📄 {DEMO_CONFIG["daily_limits"]["max_files"]} files maximum
        - 📦 {DEMO_CONFIG["daily_limits"]["max_archives"]} archives maximum  
        - 💾 {DEMO_CONFIG["daily_limits"]["max_file_size_mb"]}MB max file size
        - 📊 {DEMO_CONFIG["feature_restrictions"]["doc_level"]} documentation level only
        
        **Session Limits:**
        - 🔄 {DEMO_CONFIG["session_limits"]["max_files"]} files per session
        - 📁 {DEMO_CONFIG["session_limits"]["max_archives"]} archive per session
        
        Want unlimited access? Get your own API key at [console.anthropic.com](https://console.anthropic.com)
        """)

        return os.getenv("DEMO_KEY")

    def check_demo_limits(self, operation: str, **kwargs) -> Tuple[bool, str]:
        """
        Check if demo limits allow the requested operation.

        Args:
            operation: Type of operation ('upload', 'process', 'export')
            **kwargs: Operation-specific parameters

        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        if not st.session_state.demo_usage["is_demo_mode"]:
            return True, ""

        usage = st.session_state.demo_usage

        if operation == "upload":
            return self._check_upload_limits(kwargs.get("file_size", 0))

        elif operation == "process":
            return self._check_processing_limits(
                kwargs.get("file_count", 0), kwargs.get("total_size", 0)
            )

        elif operation == "export":
            return self._check_export_limits(kwargs.get("format", "markdown"))

        return True, ""

    def _check_upload_limits(self, file_size: int) -> Tuple[bool, str]:
        """Check upload-specific limits."""
        usage = st.session_state.demo_usage

        # Check daily archive limit
        if usage["daily_archives"] > DEMO_CONFIG["daily_limits"]["max_archives"]:
            return (
                False,
                f"Daily limit reached: {DEMO_CONFIG['daily_limits']['max_archives']} archives per day",
            )

        # Check session archive limit
        if usage["session_archives"] > DEMO_CONFIG["session_limits"]["max_archives"]:
            return (
                False,
                f"Session limit reached: {DEMO_CONFIG['session_limits']['max_archives']} archive per session",
            )

        # Check file size
        max_size = DEMO_CONFIG["daily_limits"]["max_file_size_mb"] * 1024 * 1024
        if file_size > max_size:
            return (
                False,
                f"File too large for demo: {file_size / 1024 / 1024:.1f}MB > {DEMO_CONFIG['daily_limits']['max_file_size_mb']}MB",
            )

        return True, ""

    def _check_processing_limits(
        self, file_count: int, total_size: int
    ) -> Tuple[bool, str]:
        """Check processing-specific limits."""
        usage = st.session_state.demo_usage

        # Check daily file limit
        if usage["daily_files"] + file_count > DEMO_CONFIG["daily_limits"]["max_files"]:
            remaining = DEMO_CONFIG["daily_limits"]["max_files"] - usage["daily_files"]
            return (
                False,
                f"Daily file limit exceeded: {file_count} files requested, {remaining} remaining",
            )

        # Check session file limit
        if (
            usage["session_files"] + file_count
            > DEMO_CONFIG["session_limits"]["max_files"]
        ):
            remaining = (
                DEMO_CONFIG["session_limits"]["max_files"] - usage["session_files"]
            )
            return (
                False,
                f"Session file limit exceeded: {file_count} files requested, {remaining} remaining",
            )

        # Check total size limit
        daily_size_limit = (
            DEMO_CONFIG["daily_limits"]["max_total_size_mb"] * 1024 * 1024
        )
        if usage["daily_size"] + total_size > daily_size_limit:
            return (
                False,
                f"Daily size limit exceeded: {total_size / 1024 / 1024:.1f}MB would exceed daily limit",
            )

        return True, ""

    def _check_export_limits(self, export_format: str) -> Tuple[bool, str]:
        """Check export-specific limits."""
        allowed_formats = DEMO_CONFIG["feature_restrictions"]["export_formats"]
        if export_format.lower() not in allowed_formats:
            return (
                False,
                f"Export format '{export_format}' not available in demo mode. Available: {', '.join(allowed_formats)}",
            )

        return True, ""

    def update_usage(self, operation: str, **kwargs):
        """Update usage statistics after successful operation."""
        if not st.session_state.demo_usage["is_demo_mode"]:
            return

        usage = st.session_state.demo_usage

        if operation == "upload":
            usage["daily_archives"] += 1
            usage["session_archives"] += 1

        elif operation == "process":
            file_count = kwargs.get("file_count", 0)
            total_size = kwargs.get("total_size", 0)

            usage["daily_files"] += file_count
            usage["session_files"] += file_count
            usage["daily_size"] += total_size
            usage["session_size"] += total_size

    def get_demo_status(self) -> Dict[str, Any]:
        """Get current demo usage status for display."""
        if not st.session_state.demo_usage["is_demo_mode"]:
            return {}

        usage = st.session_state.demo_usage
        daily_limits = DEMO_CONFIG["daily_limits"]
        session_limits = DEMO_CONFIG["session_limits"]

        return {
            "daily_files_used": usage["daily_files"],
            "daily_files_limit": daily_limits["max_files"],
            "daily_archives_used": usage["daily_archives"],
            "daily_archives_limit": daily_limits["max_archives"],
            "session_files_used": usage["session_files"],
            "session_files_limit": session_limits["max_files"],
            "session_archives_used": usage["session_archives"],
            "session_archives_limit": session_limits["max_archives"],
            "daily_size_used_mb": usage["daily_size"] / 1024 / 1024,
            "daily_size_limit_mb": daily_limits["max_total_size_mb"],
        }

    def apply_demo_restrictions(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply demo restrictions to configuration."""
        if not st.session_state.demo_usage["is_demo_mode"]:
            return config

        # Apply feature restrictions
        restrictions = DEMO_CONFIG["feature_restrictions"]
        demo_config = config.copy()

        # Force basic documentation level
        demo_config["doc_level"] = restrictions["doc_level"]

        # Disable concurrent processing
        if not restrictions["concurrent_mode"]:
            demo_config["concurrency_method"] = "Sequential"

        # Apply file size restrictions
        demo_config["max_file_size"] = min(
            demo_config.get("max_file_size", 5),
            DEMO_CONFIG["daily_limits"]["max_file_size_mb"],
        )

        return demo_config


def get_api_key_ui_for_demo() -> Optional[str]:
    """
    Get the API key from environment, Streamlit secrets, user input, or demo password.
    UI-specific version to avoid circular imports.

    Returns:
        API key string or None if not available
    """

    demo_manager = DemoManager()

    # Try environment variable first
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if api_key:
        st.sidebar.success("API key loaded from environment")
        return api_key

    # Check session state
    if "anthropic_api_key" in st.session_state:
        stored_key = st.session_state.anthropic_api_key

        # Check if it's a demo key
        if demo_manager.is_demo_trigger(stored_key):
            actual_key = demo_manager.activate_demo_mode(stored_key)
            return actual_key
        else:
            st.sidebar.info("API key loaded from session state")
            return stored_key

    # Get user input
    user_input = st.text_input(
        "Enter your Anthropic API Key (or 'demo' for demo mode):",
        type="password",
        help="Get your API key at console.anthropic.com or enter 'demo' to try it out",
        placeholder="sk-ant-... or 'demo'",
    )

    if user_input:
        # Check if it's a demo trigger
        if demo_manager.is_demo_trigger(user_input):
            st.session_state.anthropic_api_key = user_input
            actual_key = demo_manager.activate_demo_mode(user_input)
            return actual_key
        else:
            st.session_state.anthropic_api_key = user_input
            return user_input

    return None



def display_demo_status_sidebar():
    """Display demo status in sidebar."""
    demo_manager = DemoManager()
    status = demo_manager.get_demo_status()

    if not status:
        return

    st.sidebar.markdown("---")
    st.sidebar.subheader("🎭 Demo Mode Status")

    # Daily limits
    st.sidebar.write("**Daily Usage:**")
    st.sidebar.progress(
        status["daily_files_used"] / status["daily_files_limit"],
        text=f"Files: {status['daily_files_used']}/{status['daily_files_limit']}",
    )
    st.sidebar.progress(
        status["daily_archives_used"] / status["daily_archives_limit"],
        text=f"Archives: {status['daily_archives_used']}/{status['daily_archives_limit']}",
    )

    # Session limits
    st.sidebar.write("**Session Usage:**")
    st.sidebar.progress(
        status["session_files_used"] / status["session_files_limit"],
        text=f"Files: {status['session_files_used']}/{status['session_files_limit']}",
    )

    # Size usage
    size_progress = min(
        status["daily_size_used_mb"] / status["daily_size_limit_mb"], 1.0
    )
    st.sidebar.progress(
        size_progress,
        text=f"Size: {status['daily_size_used_mb']:.1f}/{status['daily_size_limit_mb']}MB",
    )

    # Upgrade prompt
    st.sidebar.info(
        "💡 Want unlimited access? Get your API key at [console.anthropic.com](https://console.anthropic.com)"
    )
    st.sidebar.markdown("---")


def check_demo_operation(operation: str, **kwargs) -> bool:
    """
    Check if demo limits allow operation. Use before processing.

    Returns:
        bool: True if operation is allowed
    """
    demo_manager = DemoManager()
    allowed, reason = demo_manager.check_demo_limits(operation, **kwargs)

    if not allowed:
        st.error(f"🎭 Demo Limit Reached: {reason}")
        st.info("💡 Upgrade to a full API key for unlimited access!")
        return False

    return True


def update_demo_usage(operation: str, **kwargs):
    """Update demo usage after successful operation."""
    demo_manager = DemoManager()
    demo_manager.update_usage(operation, **kwargs)


def apply_demo_config_restrictions(config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply demo restrictions to config."""
    demo_manager = DemoManager()
    return demo_manager.apply_demo_restrictions(config)
