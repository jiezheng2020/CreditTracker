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
from datetime import datetime, timedelta
from typing import List, Dict, Any

from storage import load_cards, save_cards
import os
import json
from models import Card
from plotly import graph_objects as go


# Page config
st.set_page_config(
    page_title="Credit Card Status Tracker",
    page_icon=None,
    layout="wide",
)
# Inject United Airlines–style light theme CSS
_CUSTOM_CSS = """
<style>
    :root{
        --united-blue:#005DAA; /* United Blue */
        --united-navy:#002244; /* Header/accents */
        --sky-blue:#78B9F9;   /* Optional accent */
        --text:#0f172a;       /* Slate-900 */
        --muted:#475569;      /* Slate-600 */
        --bg:#f7f9fc;         /* Very light background */
        --ring-bg:#e6e9ef;    /* Light gray ring background */
    }
    .stApp{
        font-family: Inter, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
        background: var(--bg);
        color: var(--text);
    }
    .st-emotion-cache-155jwzh {
        background-color: #005DAA;}
    summary.st-emotion-cache-11ofl8m.e1326t814 {
        background-color: #005DAA;
        color: white;}
    div.st-emotion-cache-yty0fn {
        border: solid #0000007d 1px;
        border-radius: 0 0 5px 5px; }
        /* Make Streamlit Selectbox match input styling */
    /* Hide Streamlit chrome (top black bar/menu/footer) */
    #MainMenu{visibility:hidden;}
    footer{visibility:hidden;}
    header{visibility:hidden;}
    div[data-testid="stDecoration"]{display:none;}
    div[data-testid="stToolbar"]{display:none;}
    h1, h2, h3, .stMarkdown h2{ color: var(--united-blue); }
    div.st-c1.st-bv.st-dc.st-eu.st-ev.st-ae.st-au.st-db.st-c2.st-d2.st-d3.st-d4.st-d5{
    background-color: #fff !important;
    color: #000 !important; }
    div.st-c1.st-bv.st-dg.st-eu.st-ev.st-ae.st-au.st-df.st-c2.st-d2.st-d3.st-d4.st-d5{
    background-color: #fff !important;
    color: #000 !important; }
    div.st-ay.st-af.st-ai.st-eu.st-ev.st-ag.st-b0.st-ah.st-dw.st-ei.st-ej.st-ek.st-el{
    background-color: #fff !important;
    color: #000 !important; }
    /* Buttons */
    .stButton>button{
        background: var(--united-blue);
        color: #fff;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }
    button.st-emotion-cache-zh4rd8.etdmgzm2{
        background: #fff; }
    .stButton>button:hover{ background:#0a6ed1; }
    /* Inputs */
    input, textarea, select, .stNumberInput input{
        border: 1px solid #cbd5e1 !important;
        background: #fff !important;
        color: var(--text) !important;
    }
    input.st-bp.st-bq.st-br.st-d7.st-bt.st-bu.st-bo.st-f3.st-fm.st-cz.st-do.st-cu.st-cw.st-cv.st-cx.st-b0.st-f0.st-b7.st-ao.st-aq.st-b6.st-b4.st-bi.st-bk.st-ar.st-bj{
    border: #fff !important;
    }
    label{ color: var(--text) !important; font-weight:600; }
    ::placeholder{ color:#64748b; opacity:1; }
    input:focus, textarea:focus{ outline: 2px solid var(--sky-blue) !important; }
    /* Tabs/sections */
    .stTabs [data-baseweb="tab"]{ font-weight: 600; color: var(--united-navy); }
    .block-container{ padding-top: 1rem; }
    /* Tables */
    .stDataFrame, .stTable{ box-shadow: 0 2px 8px rgba(0,0,0,0.05); border-radius: 10px; }
</style>
"""
st.markdown(_CUSTOM_CSS, unsafe_allow_html=True)

# Colors for visuals (United style)
UNITED_BLUE = "#005DAA"
UNITED_NAVY = "#002244"
SKY_BLUE = "#78B9F9"
LIGHT_RING = "#e6e9ef"


def build_ring_figure(value: float, goal: float, title: str, color: str = UNITED_BLUE, height: int = 260) -> go.Figure:
    """Return a Plotly donut-style ring that shows value progress toward goal.
    The ring is clamped at 100% fill while still displaying the full numeric value.
    """
    goal = max(1, int(goal))
    clamped = max(0, min(value, goal))
    remaining = max(goal - clamped, 0.0001)

    fig = go.Figure(
        data=[
            go.Pie(
                values=[clamped, remaining],
                hole=0.75,
                sort=False,
                direction="clockwise",
                marker=dict(colors=[color, LIGHT_RING], line=dict(width=0)),
                textinfo="none",
                hoverinfo="skip",
            )
        ]
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        height=height,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
    )
    # Center annotations: value, label, and of goal
    fig.add_annotation(
        text=f"<b>{int(value):,}</b>",
        x=0.5, y=0.58, showarrow=False, font=dict(size=22, color="#0f172a"), align="center"
    )
    fig.add_annotation(
        text=f"<span style='color:#475569'>{title}</span>",
        x=0.5, y=0.42, showarrow=False, font=dict(size=13), align="center"
    )
    fig.add_annotation(
        text=f"<span style='color:#64748b'>of {int(goal):,}</span>",
        x=0.5, y=0.28, showarrow=False, font=dict(size=12), align="center"
    )
    return fig
if "save_message" not in st.session_state:
    st.session_state.save_message = None


def normalize_card(card: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a card dict to have all required fields.
    Used for backward compatibility with old JSON files.
    """
    return {
        "card_name": card.get("card_name", "Unknown"),
        "welcome_points": card.get("welcome_points", 0),
        "opened_date": card.get("opened_date", ""),
        "issuer": card.get("issuer", "Unknown"),
        "benefits": card.get("benefits", ""),
    }


def normalize_wishlist_card(card: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a wishlist card dict to have all required fields.
    """
    return {
        "card_name": card.get("card_name", "Unknown"),
        "issuer": card.get("issuer", "Unknown"),
        "target_points": card.get("target_points", 0),
        "notes": card.get("notes", ""),
    }


def parse_json_data(data: Any) -> tuple[List[Dict], List[Dict]]:
    """
    Parse JSON data and extract current cards and wishlist.

    Handles both old format (just a list of current cards)
    and new format (dict with "current" and "wishlist" keys).
    """
    current_cards = []
    wishlist_cards = []

    if isinstance(data, list):
        # Old format: just a list of cards
        current_cards = [normalize_card(c) for c in data]
    elif isinstance(data, dict):
        # New format with current and/or wishlist
        if "current" in data and isinstance(data["current"], list):
            current_cards = [normalize_card(c) for c in data["current"]]
        elif not isinstance(data.get("current"), dict):  # If data is a card dict, treat it as current
            current_cards = [normalize_card(data)]

        if "wishlist" in data and isinstance(data["wishlist"], list):
            wishlist_cards = [normalize_wishlist_card(c) for c in data["wishlist"]]

    return current_cards, wishlist_cards


def export_json_data(current_cards: List[Dict], wishlist_cards: List[Dict]) -> str:
    """
    Export current cards and wishlist to JSON format.
    Uses new format: {"current": [...], "wishlist": [...]}
    """
    data = {
        "current": current_cards,
        "wishlist": wishlist_cards,
    }
    return json.dumps(data, indent=2)


def save_to_file() -> None:
    """Save current and wishlist cards to the local `db_path` stored in session state.

    Writes the new-format JSON produced by `export_json_data`. On success sets
    `st.session_state.save_message` to a success string, on error sets an error
    message and logs the exception.
    """
    try:
        # Derive a sensible default path based on OS selection if not present
        os_sel = st.session_state.get("os_selection", "Windows")
        default_path = (
            os.path.expanduser("~/Desktop/cards.json")
            if os_sel == "Windows"
            else os.path.expanduser("~/Library/Application Support/CardTracker/cards.json")
        )
        db_path = st.session_state.get("db_path", default_path)

        json_export = export_json_data(st.session_state.get("current_cards", []), st.session_state.get("wishlist_cards", []))
        # Ensure parent directory exists
        parent = os.path.dirname(db_path)
        if parent and not os.path.exists(parent):
            os.makedirs(parent, exist_ok=True)

        with open(db_path, "w", encoding="utf-8") as f:
            f.write(json_export)

        st.session_state.save_message = f"Saved to {db_path}"
    except Exception as e:
        st.session_state.save_message = f"Error saving file: {e}"
        raise


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


def count_chase_5_24() -> tuple[int, str]:
    """
    Count Chase cards opened in the last 24 months for 5/24 rule.

    Returns:
        (count, next_drop_off_date_str)
    """
    current_cards = st.session_state.get("current_cards", [])
    now = datetime.now()
    cutoff = now - timedelta(days=730)  # 24 months

    count = 0
    oldest_date = None

    for card in current_cards:
        issuer = (card.get("issuer") or "").strip()
        # Match Chase case-insensitively and allow variants like 'Chase Bank'
        if "chase" in issuer.lower():
            date_str = (card.get("opened_date") or "").strip()
            if not date_str:
                continue
            # Try several common date formats (ISO and US common)
            parsed = None
            for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d", "%m-%d-%Y"):
                try:
                    parsed = datetime.strptime(date_str, fmt)
                    break
                except Exception:
                    continue
            if parsed is None:
                # couldn't parse date
                continue
            opened = parsed
            if opened >= cutoff:
                count += 1
                if oldest_date is None or opened < oldest_date:
                    oldest_date = opened

    # Calculate next drop-off date
    if oldest_date:
        next_drop = oldest_date + timedelta(days=730)
        next_drop_str = next_drop.strftime("%Y-%m-%d")
    else:
        next_drop_str = "N/A"

    return count, next_drop_str


def total_welcome_points() -> int:
    """Sum of all welcome points from current cards."""
    current_cards = st.session_state.get("current_cards", [])
    return sum(card.get("welcome_points", 0) for card in current_cards)


def total_wishlist_points() -> int:
    """Sum of all target points from wishlist cards."""
    wishlist_cards = st.session_state.get("wishlist_cards", [])
    return sum(card.get("target_points", 0) for card in wishlist_cards)


def main() -> None:
    """Main app logic with all four features."""
    st.title("Credit Card Status Tracker")
    st.markdown("Track current cards, 5/24 rule, points, and wishlist.")

    # Initialize session state
    if "current_cards" not in st.session_state:
        st.session_state.current_cards = []
    if "wishlist_cards" not in st.session_state:
        st.session_state.wishlist_cards = []
    if "points_goal" not in st.session_state:
        st.session_state.points_goal = 200000

    # OS detection
    if "os_selection" not in st.session_state:
        st.session_state.os_selection = "Windows"

    st.sidebar.header("Settings")
    st.sidebar.radio(
        "Select your operating system:",
        ["Windows", "Mac"],
        key="os_selection"
    )

    DEFAULT_DB_PATH = (
        os.path.expanduser("~/Desktop/cards.json")
        if st.session_state.os_selection == "Windows"
        else os.path.expanduser("~/Library/Application Support/CardTracker/cards.json")
    )

    # Data source selection
    st.markdown("## Data Source")
    col_local, col_upload = st.columns([1, 1])

    with col_local:
        st.subheader("Local File")
        db_path_input = st.text_input(
            "File path",
            value=DEFAULT_DB_PATH,
            key="db_path_input",
        )

    with col_upload:
        st.subheader("Upload & Download")
        uploaded_file = st.file_uploader("Upload cards.json", type=["json"], key="uploaded_file")

    # Load data
    if "mode" not in st.session_state:
        if uploaded_file:
            try:
                data = json.loads(uploaded_file.read().decode("utf-8"))
                current, wishlist = parse_json_data(data)
                st.session_state.current_cards = current
                st.session_state.wishlist_cards = wishlist
                st.session_state.mode = "uploaded"
            except Exception as e:
                st.error(f"Could not parse uploaded file: {e}")
                st.session_state.mode = "uploaded"
        else:
            db_path = db_path_input or DEFAULT_DB_PATH
            st.session_state.db_path = db_path
            try:
                if os.path.exists(db_path):
                    with open(db_path, 'r') as f:
                        data = json.load(f)
                    current, wishlist = parse_json_data(data)
                    st.session_state.current_cards = current
                    st.session_state.wishlist_cards = wishlist
            except Exception:
                pass
            st.session_state.mode = "local"
    else:
        # Handle mode switching
        if uploaded_file and st.session_state.get("mode") != "uploaded":
            try:
                data = json.loads(uploaded_file.read().decode("utf-8"))
                current, wishlist = parse_json_data(data)
                st.session_state.current_cards = current
                st.session_state.wishlist_cards = wishlist
                st.session_state.mode = "uploaded"
            except Exception:
                pass
        elif not uploaded_file and st.session_state.get("mode") != "local":
            db_path = db_path_input or DEFAULT_DB_PATH
            st.session_state.db_path = db_path
            try:
                if os.path.exists(db_path):
                    with open(db_path, 'r') as f:
                        data = json.load(f)
                    current, wishlist = parse_json_data(data)
                    st.session_state.current_cards = current
                    st.session_state.wishlist_cards = wishlist
            except Exception:
                pass
            st.session_state.mode = "local"

    # FEATURE 1: Status / Progress (United-style rings)
    st.markdown("---")
    st.markdown("## Status / Progress")

    # Compute values
    chase_count, next_drop = count_chase_5_24()
    total_pts = total_welcome_points()
    wish_pts = total_wishlist_points()
    goal = st.session_state.points_goal

    col_points, col_5_24, col_wishlist = st.columns(3)

    with col_points:
        fig = build_ring_figure(total_pts, goal, "Total Points", color=UNITED_BLUE, height=270)
        st.plotly_chart(fig, config={"displayModeBar": False}, width="stretch")
        st.number_input(
            "Points goal",
            min_value=0,
            step=10000,
            key="points_goal",
        )

    with col_5_24:
        fig = build_ring_figure(chase_count, 5, "Chase 5/24", color=SKY_BLUE, height=270)
        st.plotly_chart(fig, config={"displayModeBar": False}, width="stretch")
        st.caption(f"Next drop: {next_drop}")

    with col_wishlist:
        fig = build_ring_figure(wish_pts, max(goal, 1), "Wishlist Potential", color=UNITED_NAVY, height=270)
        st.plotly_chart(fig, config={"displayModeBar": False}, width="stretch")

    # FEATURE 1: Main content with tabs (Current vs Wishlist)
    st.markdown("---")
    tab_current, tab_wishlist = st.tabs(["Current Cards", "Wishlist"])

    with tab_current:
        st.header("Current Cards")

        # Display current cards
        if st.session_state.current_cards:
            col_delete, col_name, col_issuer, col_pts, col_date = st.columns([0.5, 2, 1.5, 1.5, 1.5])
            with col_delete:
                st.write("**Action**")
            with col_name:
                st.write("**Name**")
            with col_issuer:
                st.write("**Issuer**")
            with col_pts:
                st.write("**Points**")
            with col_date:
                st.write("**Opened**")

            for idx, card in enumerate(st.session_state.current_cards):
                col_delete, col_name, col_issuer, col_pts, col_date = st.columns([0.5, 2, 1.5, 1.5, 1.5])
                with col_delete:
                    if st.button("❌", key=f"del_current_{idx}"):
                        st.session_state.current_cards.pop(idx)
                        st.rerun()
                with col_name:
                    st.write(card["card_name"])
                with col_issuer:
                    st.write(card.get("issuer", "N/A"))
                with col_pts:
                    st.write(f"{card.get('welcome_points', 0):,}")
                with col_date:
                    st.write(card.get("opened_date", "N/A"))

            # FEATURE 2: Detail view
            st.subheader("Card Details")
            detail_idx = st.selectbox(
                "Select a card",
                range(len(st.session_state.current_cards)),
                format_func=lambda i: st.session_state.current_cards[i]["card_name"],
                key="current_detail_idx"
            )

            if detail_idx < len(st.session_state.current_cards):
                card = st.session_state.current_cards[detail_idx]
                with st.expander(f"Details: {card['card_name']}", expanded=True):
                    col_detail_1, col_detail_2 = st.columns(2)
                    with col_detail_1:
                        st.write(f"**Issuer:** {card.get('issuer', 'N/A')}")
                        st.write(f"**Opened:** {card.get('opened_date', 'N/A')}")
                    with col_detail_2:
                        st.write(f"**Welcome Points:** {card.get('welcome_points', 0):,}")
                    st.write("**Benefits/Credits:**")
                    st.write(card.get("benefits", "(None)"))
        else:
            st.info("No current cards yet.")

        # Add current card form
        st.subheader("Add Current Card")
        col_name, col_date = st.columns(2)
        with col_name:
            add_name = st.text_input("Card Name", key="add_card_name")
        with col_date:
            add_date = st.text_input("Opened Date (YYYY-MM-DD)", key="add_card_date")

        col_issuer, col_pts = st.columns(2)
        with col_issuer:
            add_issuer = st.selectbox(
                "Issuer",
                ["Chase", "American Express", "Capital One", "Citi", "Bank of America", "US Bank", "Other"],
                key="add_card_issuer"
            )
        with col_pts:
            add_points = st.number_input("Welcome Points", min_value=0, step=100, key="add_card_points")

        add_benefits = st.text_area("Benefits/Credits", key="add_card_benefits", height=80)

        if st.button("Add Card", key="btn_add_card", width="stretch"):
            errors = []
            if not add_name or not add_name.strip():
                errors.append("Card name required")
            if not add_date or not add_date.strip():
                errors.append("Date required (YYYY-MM-DD)")
            elif not validate_date(add_date.strip()):
                errors.append("Invalid date format")

            if errors:
                for err in errors:
                    st.error(err)
            else:
                new_card = {
                    "card_name": add_name.strip(),
                    "opened_date": add_date.strip(),
                    "issuer": add_issuer,
                    "welcome_points": int(add_points),
                    "benefits": add_benefits.strip() or ""
                }
                st.session_state.current_cards.append(new_card)
                st.success(f"Added {add_name}!")
                st.rerun()

    with tab_wishlist:
        st.header("Wishlist")
        st.markdown("Cards you plan to apply for")

        # Display wishlist cards
        if st.session_state.wishlist_cards:
            col_delete, col_name, col_issuer, col_pts = st.columns([0.5, 2, 1.5, 2])
            with col_delete:
                st.write("**Action**")
            with col_name:
                st.write("**Name**")
            with col_issuer:
                st.write("**Issuer**")
            with col_pts:
                st.write("**Target Points**")

            for idx, card in enumerate(st.session_state.wishlist_cards):
                col_delete, col_name, col_issuer, col_pts = st.columns([0.5, 2, 1.5, 2])
                with col_delete:
                    if st.button("❌", key=f"del_wish_{idx}"):
                        st.session_state.wishlist_cards.pop(idx)
                        st.rerun()
                with col_name:
                    st.write(card["card_name"])
                with col_issuer:
                    st.write(card.get("issuer", "N/A"))
                with col_pts:
                    st.write(f"{card.get('target_points', 0):,}")

            # Detail view for wishlist
            st.subheader("Card Details")
            wish_detail_idx = st.selectbox(
                "Select a card",
                range(len(st.session_state.wishlist_cards)),
                format_func=lambda i: st.session_state.wishlist_cards[i]["card_name"],
                key="wish_detail_idx"
            )

            if wish_detail_idx < len(st.session_state.wishlist_cards):
                card = st.session_state.wishlist_cards[wish_detail_idx]
                with st.expander(f"Details: {card['card_name']}", expanded=True):
                    st.write(f"**Issuer:** {card.get('issuer', 'N/A')}")
                    st.write(f"**Target Points:** {card.get('target_points', 0):,}")
                    st.write("**Notes:**")
                    st.write(card.get("notes", "(None)"))
        else:
            st.info("Wishlist is empty.")

        # Add wishlist card form
        st.subheader("Add Wishlist Card")
        col_name, col_issuer = st.columns(2)
        with col_name:
            wish_name = st.text_input("Card Name", key="wish_card_name")
        with col_issuer:
            wish_issuer = st.selectbox(
                "Issuer",
                ["Chase", "American Express", "Capital One", "Citi", "Bank of America", "US Bank", "Other"],
                key="wish_card_issuer"
            )

        col_pts, _ = st.columns(2)
        with col_pts:
            wish_pts = st.number_input("Target Points", min_value=0, step=1000, key="wish_card_points")

        wish_notes = st.text_area("Notes", key="wish_card_notes", height=80)

        if st.button("Add to Wishlist", key="btn_add_wish", width="stretch"):
            if not wish_name or not wish_name.strip():
                st.error("Card name required")
            else:
                wish_card = {
                    "card_name": wish_name.strip(),
                    "issuer": wish_issuer,
                    "target_points": int(wish_pts),
                    "notes": wish_notes.strip() or ""
                }
                st.session_state.wishlist_cards.append(wish_card)
                st.success(f"Added {wish_name} to wishlist!")
                st.rerun()

    # Save/Download section
    st.markdown("---")
    st.header("Save Your Data")

    if st.session_state.save_message:
        st.success(st.session_state.save_message)
        st.session_state.save_message = None

    if uploaded_file:
        st.markdown("### Download Mode")
        json_export = export_json_data(st.session_state.current_cards, st.session_state.wishlist_cards)
        col_dl, col_info = st.columns([2, 1])
        with col_dl:
            st.download_button(
                "Download cards.json",
                data=json_export,
                file_name="cards.json",
                mime="application/json",
                width="stretch"
            )
        with col_info:
            if st.button("Info", key="info_dl"):
                st.info("Download to save your updated file.")
    else:
        st.markdown("### Local File Mode")
        st.markdown(f"Saving to: `{st.session_state.get('db_path', DEFAULT_DB_PATH)}`")
        col_save, col_info = st.columns([2, 1])
        with col_save:
            if st.button("Save", key="btn_save", width="stretch"):
                save_to_file()
        with col_info:
            if st.button("Info", key="info_save"):
                st.info("Save your cards to your computer.")

    st.divider()
    st.caption("Credit Card Welcome Bonus Tracker v2")


if __name__ == "__main__":
    main()
