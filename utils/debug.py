import streamlit as st

def show_debug_info():
    """Show debug information in sidebar."""
    with st.expander("🐛 Debug Info", expanded=False):
        st.write("**Session State:**")
        
        if st.session_state:
            for key, value in st.session_state.items():
                # Mask sensitive data
                if "api" in key.lower() or "key" in key.lower():
                    if isinstance(value, str) and len(value) > 10:
                        display_value = f"{value[:8]}...{value[-4:]}"
                    else:
                        display_value = value
                else:
                    display_value = value
                
                st.write(f"• {key}: {display_value}")
        else:
            st.write("Empty session state")
        
        # Button to clear session state
        if st.button("🗑️ Clear Session State"):
            st.session_state.clear()
            st.rerun()