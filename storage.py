"""
Storage module for managing credit card data persistence.
Handles loading and saving cards to/from a JSON file.
"""

import json
import os
from typing import List

from models import Card


def load_cards(file_path: str) -> List[Card]:
    """
    Load cards from a JSON file.

    If the file does not exist or is empty, returns an empty list.
    If the JSON is malformed, prints an error and returns an empty list.

    Args:
        file_path: Path to the JSON file storing card data

    Returns:
        A list of Card dictionaries
    """
    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, 'r') as f:
            content = f.read().strip()
            if not content:
                return []
            cards = json.loads(content)
            return cards if isinstance(cards, list) else []
    except json.JSONDecodeError:
        print(f"⚠️  Error: {file_path} contains invalid JSON. Starting with an empty list.")
        return []
    except Exception as e:
        print(f"⚠️  Error reading {file_path}: {e}. Starting with an empty list.")
        return []


def save_cards(file_path: str, cards: List[Card]) -> None:
    """
    Save cards to a JSON file.

    Writes the cards list as formatted JSON. Safe to call multiple times.

    Args:
        file_path: Path to the JSON file where card data will be stored
        cards: List of Card dictionaries to persist
    """
    try:
        with open(file_path, 'w') as f:
            json.dump(cards, f, indent=2)
    except Exception as e:
        print(f"❌ Error saving to {file_path}: {e}")
        raise
