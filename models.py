"""
Data models for the Credit Card Welcome Bonus Tracker.
"""

from typing import TypedDict


class Card(TypedDict):
    """
    Represents a credit card with welcome bonus tracking information.

    Attributes:
        card_name: The name of the credit card (e.g., "Chase Sapphire Preferred")
        welcome_points: The number of welcome bonus points offered
        opened_date: The date the card was opened in ISO format (YYYY-MM-DD)
    """
    card_name: str
    welcome_points: int
    opened_date: str
