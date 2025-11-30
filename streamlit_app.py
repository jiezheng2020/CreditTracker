"""
Streamlit web app for the Credit Card Welcome Bonus Tracker.

This app provides a web-based UI for tracking credit card welcome offers.
It reuses storage.py and models.py for data persistence and structure.

Run locally with:
    streamlit run streamlit_app.py

Deploy to Streamlit Community Cloud:
    1. Push your project to GitHub (including this file, storage.py, models.py, requirements.txt, .gitignore)
    2. Go to https://share.streamlit.io/
    3. Connect your GitHub repo and select this file as the main file
    4. Streamlit will automatically deploy and provide a public URL

Deploy to Hugging Face Spaces:
    1. Create a new Space with a Streamlit app template
    2. Push your files to the Space's repo
    3. HF will automatically deploy and provide a URL
"""

import streamlit as st
from datetime import datetime
from typing import List

from storage import load_cards, save_cards
import os
import json
from models import Card


# Page config
st.set_page_config(
    page_title="Credit Card Welcome Bonus Tracker",
    page_icon="💳",
    layout="wide",
)

if "save_message" not in st.session_state:
    st.session_state.save_message = None


def validate_date(date_str: str) -> bool:
    """
    Validate that a date string is in ISO format (YYYY-MM-DD).

    Args:
        date_str: Date string to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def add_card_to_list(
    card_name: str,
    welcome_points: int,
    opened_date: str,
) -> bool:
    """
    Add a new card to the session state list with validation.

    Args:
        card_name: Name of the card
        welcome_points: Welcome bonus points
        opened_date: Date opened in YYYY-MM-DD format

    Returns:
        True if successful, False otherwise
    """
    # Validate card name
    if not card_name or not card_name.strip():
        st.error("❌ Card name cannot be empty.")
        return False

    # Validate welcome points
    try:
        points = int(welcome_points)
        if points <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        st.error("❌ Welcome points must be a positive integer.")
        return False

    # Validate date
    if not validate_date(opened_date):
        st.error("❌ Date must be in YYYY-MM-DD format (e.g., 2025-11-28).")
        return False

    # Create and add card
    new_card: Card = {
        "card_name": card_name.strip(),
        "welcome_points": points,
        "opened_date": opened_date,
    }
    st.session_state.cards.append(new_card)
    st.success(f"✅ Card '{card_name.strip()}' added successfully!")
    return True


def save_to_file() -> None:
    """Save the current cards list to the configured local DB path.

    This writes to the local filesystem only (local mode). In uploaded (online) mode
    this function should not be called to persist to server storage.
    """
    # Prefer reading the current input widget value so changes to the text input are respected
    db_path = st.session_state.get("db_path_input", os.path.expanduser("~/Desktop/cards.json"))
    # Ensure parent directory exists (attempt to create it). On hosted services this may fail.
    parent = os.path.dirname(os.path.abspath(db_path))
    try:
        if parent and not os.path.exists(parent):
            os.makedirs(parent, exist_ok=True)
    except Exception as e:
        st.error(f"❌ Cannot create directory for {db_path}: {e}")
        return

    try:
        save_cards(db_path, st.session_state.cards)
        st.session_state.save_message = f"✅ Cards saved to {db_path}"
    except Exception as e:
        # Provide a clearer message for common server-side situations
        if isinstance(e, FileNotFoundError):
            st.error(
                f"❌ Error saving: target path {db_path} not found. On hosted deployments (Streamlit Cloud) writing to \"~/Desktop\" may not be allowed.\n"
                "Use the upload/download flow instead, or choose a writable local path when running locally."
            )
        else:
            st.error(f"❌ Error saving: {e}")


def main() -> None:
    """Main app logic."""
    # Title
    st.title("💳 Credit Card Welcome Bonus Tracker")
    st.markdown("Track your credit card welcome offers and bonus points in one place.")

    # OS detection for correct file paths - store in session_state to trigger updates
    if "os_selection" not in st.session_state:
        st.session_state.os_selection = "Windows"

    st.sidebar.header("⚙️ Settings")
    os_selection = st.sidebar.radio(
        "Select your operating system:",
        ["Windows", "Mac"],
        key="os_selection"
    )

    # Determine DEFAULT_DB_PATH based on OS selection (use session_state so changes trigger rerun)
    if st.session_state.os_selection == "Windows":
        DEFAULT_DB_PATH = os.path.expanduser("~/Desktop/cards.json")
    else:  # Mac
        DEFAULT_DB_PATH = os.path.expanduser("~/Library/Application Support/CardTracker/cards.json")

    # Mode selection: uploaded file (online) OR local DB path
    st.markdown("## 📂 Data Source")
    st.markdown("**Choose how to store your cards:**")

    col_mode_1, col_mode_2 = st.columns([1, 1])
    with col_mode_1:
        st.subheader("💾 Local File")
        st.markdown("Save to your computer")
        db_path_input = st.text_input(
            "File path (default: " + ("Desktop" if st.session_state.os_selection == "Windows" else "Application Support") + ")",
            value=DEFAULT_DB_PATH,
            key="db_path_input",
            help="Recommended for local use"
        )

    with col_mode_2:
        st.subheader("☁️ Upload & Download")
        st.markdown("Use your own JSON file")
        uploaded_file = st.file_uploader(
            "Upload your cards.json",
            type=["json"],
            key="uploaded_file",
            help="For sharing or using online"
        )

    # Initialize or update session_state.cards depending on mode
    if "cards" not in st.session_state:
        # first run: decide source
        if uploaded_file is not None:
            try:
                uploaded_bytes = uploaded_file.read()
                parsed = json.loads(uploaded_bytes.decode("utf-8")) if isinstance(uploaded_bytes, (bytes, bytearray)) else json.loads(uploaded_bytes)
                st.session_state.cards = parsed if isinstance(parsed, list) else []
            except Exception:
                st.session_state.cards = []
                st.error("Uploaded file could not be parsed as JSON; starting with empty list.")
            st.session_state.mode = "uploaded"
        else:
            db_path = db_path_input or DEFAULT_DB_PATH
            st.session_state.db_path = db_path
            st.session_state.cards = load_cards(db_path)
            st.session_state.mode = "local"
    else:
        # Subsequent interactions: if user uploads a file during the session, switch to uploaded mode
        if uploaded_file is not None and st.session_state.get("mode") != "uploaded":
            try:
                uploaded_bytes = uploaded_file.read()
                parsed = json.loads(uploaded_bytes.decode("utf-8")) if isinstance(uploaded_bytes, (bytes, bytearray)) else json.loads(uploaded_bytes)
                st.session_state.cards = parsed if isinstance(parsed, list) else []
            except Exception:
                st.session_state.cards = []
                st.error("Uploaded file could not be parsed as JSON; starting with empty list.")
            st.session_state.mode = "uploaded"
        # If no upload and user changed db_path, optionally reload from that path
        elif uploaded_file is None and st.session_state.get("mode") != "local":
            db_path = db_path_input or DEFAULT_DB_PATH
            st.session_state.db_path = db_path
            st.session_state.cards = load_cards(db_path)
            st.session_state.mode = "local"

    # Display existing cards
    st.header("Your Cards")

    if st.session_state.cards:
        # Convert to list of tuples for easier display
        card_data = [
            (
                card["card_name"],
                card["welcome_points"],
                card["opened_date"],
            )
            for card in st.session_state.cards
        ]

        # Display as table
        st.dataframe(
            data={
                "Card Name": [c[0] for c in card_data],
                "Welcome Points": [c[1] for c in card_data],
                "Opened Date": [c[2] for c in card_data],
            },
            width="stretch",
            hide_index=True,
        )
    else:
        st.info("📋 No cards tracked yet. Add one below!")

    # Add new card section
    st.header("Add New Card")

    col1, col2, col3 = st.columns(3)

    with col1:
        card_name = st.text_input(
            "Card Name",
            placeholder="e.g., Chase Sapphire Preferred",
            key="input_card_name",
        )

    with col2:
        welcome_points = st.number_input(
            "Welcome Points",
            min_value=1,
            step=1000,
            key="input_points",
        )

    with col3:
        opened_date = st.text_input(
            "Opened Date (YYYY-MM-DD)",
            placeholder="e.g., 2025-11-28",
            key="input_date",
        )

    # Button row
    col1, col2 = st.columns(2)

    # Define callbacks that operate on session_state (safe for Streamlit widgets)
    def on_add() -> None:
        """Callback for Add Card button that reads values from session_state."""
        card_name_val = st.session_state.get("input_card_name", "")
        points_val = st.session_state.get("input_points", 0)
        date_val = st.session_state.get("input_date", "")

        if add_card_to_list(card_name_val, int(points_val), date_val):
            # Clear inputs by updating session_state (safe in callback)
            st.session_state["input_card_name"] = ""
            st.session_state["input_points"] = 1
            st.session_state["input_date"] = ""

    def on_delete() -> None:
        """Delete the selected card from session_state.cards."""
        sel = st.session_state.get("delete_choice")
        if sel is None:
            st.error("No card selected to delete.")
            return
        try:
            idx = int(sel)
        except Exception:
            st.error("Invalid selection")
            return

        if 0 <= idx < len(st.session_state.cards):
            card = st.session_state.cards.pop(idx)
            st.success(f"✅ Deleted '{card['card_name']}'")
        else:
            st.error("Selection out of range")

    with col1:
        st.button("➕ Add Card", key="btn_add", on_click=on_add, use_container_width=True)

    # Delete UI section
    if st.session_state.cards:
        st.markdown("---")
        st.header("🗑️ Delete Card")
        # Prepare options as index strings so selection is stable
        options = [f"{i}: {c['card_name']} — {c['welcome_points']} pts — {c['opened_date']}" for i, c in enumerate(st.session_state.cards)]
        # store choice as the index string prefix (we'll parse index)
        choice = st.selectbox("Select a card to delete", options, key="delete_select")
        # extract index from chosen option
        try:
            choice_idx = int(choice.split(":", 1)[0])
        except Exception:
            choice_idx = None
        # expose to session_state for callback
        st.session_state["delete_choice"] = choice_idx

        col_delete_1, col_delete_2 = st.columns([1, 3])
        with col_delete_1:
            if st.button("Delete", key="btn_delete", on_click=on_delete, use_container_width=True):
                # on_delete runs via callback; rerun to refresh UI
                st.experimental_rerun()
        with col_delete_2:
            st.caption("⚠️ This action cannot be undone")

    # Save/Download section - PROMINENT
    st.markdown("---")
    st.header("💾 Save Your Data")

    # Display save message if set
    if st.session_state.save_message:
        st.success(st.session_state.save_message)
        st.session_state.save_message = None

    if uploaded_file is not None:
        # UPLOADED MODE - Download is the primary action
        st.markdown("### 📥 Download Mode")
        st.markdown("Your changes are saved in this session. Download your updated file:")
        try:
            json_text = json.dumps(st.session_state.cards, indent=2)
        except Exception:
            json_text = "[]"

        col_dl_1, col_dl_2 = st.columns([2, 1])
        with col_dl_1:
            st.download_button(
                label="⬇️ Download updated cards.json",
                data=json_text,
                file_name="cards.json",
                mime="application/json",
                key="download_json",
                use_container_width=True,
            )
        with col_dl_2:
            if st.button("ℹ️ Info", key="info_uploaded"):
                st.info("💡 Your changes stay in this browser session only. Download to save your file locally.")
    else:
        # LOCAL MODE - Save to file is the primary action
        st.markdown("### 💿 Local File Mode")
        st.markdown(f"Saving to: `{st.session_state.get('db_path', DEFAULT_DB_PATH)}`")

        col_save_1, col_save_2 = st.columns([2, 1])
        with col_save_1:
            if st.button("💾 Save to Local File", key="btn_save", use_container_width=True):
                save_to_file()
        with col_save_2:
            if st.button("ℹ️ Info", key="info_local"):
                st.info("💡 Your cards are saved to your computer whenever you click 'Save to Local File'.")

    # Footer
    st.divider()
    st.caption("💳 Credit Card Welcome Bonus Tracker — Track your welcome offers easily!")


if __name__ == "__main__":
    main()
