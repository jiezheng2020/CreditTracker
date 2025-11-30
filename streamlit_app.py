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

    # Mode selection: uploaded file (online) OR local DB path
    DEFAULT_DB_PATH = os.path.expanduser("~/Desktop/cards.json")
    st.markdown("**Data source** — choose a local file path (desktop) or upload your `cards.json`.")
    col_mode_1, col_mode_2 = st.columns([3, 2])
    with col_mode_1:
        db_path_input = st.text_input("Database file path (local mode)", value=DEFAULT_DB_PATH, key="db_path_input")
    with col_mode_2:
        uploaded_file = st.file_uploader("Upload your cards.json (online mode)", type=["json"], key="uploaded_file")

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
        st.button("Add Card", key="btn_add", on_click=on_add)

    with col2:
        if st.button("Save", key="btn_save"):
            # If an uploaded file is present in this run, treat as uploaded/online mode
            if uploaded_file is not None:
                st.info("Uploaded mode: changes are in-memory only. Use the Download button to save a copy locally.")
            else:
                save_to_file()

    # Display save message if set
    if st.session_state.save_message:
        st.success(st.session_state.save_message)
        st.session_state.save_message = None

    # Simple delete UI
    if st.session_state.cards:
        st.header("Delete Card")
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
        if st.button("Delete Selected", key="btn_delete", on_click=on_delete):
            # on_delete runs via callback; rerun to refresh UI
            st.experimental_rerun()

    # If running with an uploaded file, offer a download button so users can save their updated JSON
    if st.session_state.get("mode") == "uploaded":
        try:
            json_text = json.dumps(st.session_state.cards, indent=2)
        except Exception:
            json_text = "[]"
        st.download_button(
            label="Download updated cards.json",
            data=json_text,
            file_name="cards.json",
            mime="application/json",
            key="download_json",
        )
        st.info("Uploaded mode: changes are kept in this session and can be downloaded. They are not saved to the server.")
    else:
        # show active local DB path
        dbp = st.session_state.get("db_path", os.path.expanduser("~/Desktop/cards.json"))
        st.caption(f"Data is stored locally at: {dbp}")

    # Footer
    st.divider()


if __name__ == "__main__":
    main()
