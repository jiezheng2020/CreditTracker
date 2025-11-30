"""
Main entry point for the Credit Card Welcome Bonus Tracker.
Provides a CLI menu for managing credit cards and their welcome bonuses.
"""

import os
from datetime import datetime

from models import Card
from storage import load_cards, save_cards


CARDS_FILE = "cards.json"


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


def validate_points(points_str: str) -> bool:
    """
    Validate that a string represents a positive integer.

    Args:
        points_str: String to validate

    Returns:
        True if valid positive integer, False otherwise
    """
    try:
        points = int(points_str)
        return points > 0
    except ValueError:
        return False


def list_cards(cards: list[Card]) -> None:
    """
    Display all cards in a readable format.

    Args:
        cards: List of Card dictionaries to display
    """
    if not cards:
        print("\n📋 No cards tracked yet.\n")
        return

    print("\n" + "=" * 70)
    print(f"{'Card Name':<35} {'Points':<15} {'Opened':<15}")
    print("=" * 70)

    for card in cards:
        print(f"{card['card_name']:<35} {card['welcome_points']:<15} {card['opened_date']:<15}")

    print("=" * 70)
    print(f"Total: {len(cards)} card(s)\n")


def add_card(cards: list[Card]) -> None:
    """
    Prompt user to add a new card and validate inputs.

    Args:
        cards: List to append the new card to
    """
    print("\n--- Add New Card ---")

    # Get card name
    card_name = input("Card name (e.g., Chase Sapphire Preferred): ").strip()
    if not card_name:
        print("❌ Card name cannot be empty.\n")
        return

    # Get welcome points
    while True:
        points_input = input("Welcome offer points (must be a positive number): ").strip()
        if validate_points(points_input):
            welcome_points = int(points_input)
            break
        print("❌ Invalid input. Please enter a positive integer.")

    # Get opened date
    while True:
        date_input = input("Date opened (YYYY-MM-DD, e.g., 2025-11-28): ").strip()
        if validate_date(date_input):
            opened_date = date_input
            break
        print("❌ Invalid date format. Please use YYYY-MM-DD.")

    # Create and add card
    new_card: Card = {
        "card_name": card_name,
        "welcome_points": welcome_points,
        "opened_date": opened_date,
    }
    cards.append(new_card)
    print(f"✅ Card added: {card_name}\n")


def show_menu() -> None:
    """
    Display the main CLI menu and handle user interactions.
    """
    cards = load_cards(CARDS_FILE)

    print("\n" + "=" * 70)
    print("💳 Credit Card Welcome Bonus Tracker")
    print("=" * 70)

    while True:
        print("\nOptions:")
        print("1) List cards")
        print("2) Add new card")
        print("3) Save and exit")

        choice = input("\nEnter your choice (1-3): ").strip()

        if choice == "1":
            list_cards(cards)
        elif choice == "2":
            add_card(cards)
        elif choice == "3":
            save_cards(CARDS_FILE, cards)
            print(f"✅ Data saved to {CARDS_FILE}")
            print("Goodbye!\n")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.\n")


def main() -> None:
    """Main entry point for the application."""
    try:
        show_menu()
    except KeyboardInterrupt:
        print("\n\n⚠️  Program interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
