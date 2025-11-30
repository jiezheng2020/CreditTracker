"""
Tkinter GUI for the Credit Card Welcome Bonus Tracker.

Run this file with:
    python app.py

Data is stored in cards.json. This app can be packaged as a standalone executable:
    pyinstaller --onefile app.py

The cards.json file will be created/read from the same directory as the executable.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import List

from storage import load_cards, save_cards
from models import Card


class CardTrackerApp:
    """
    Main GUI application for tracking credit card welcome bonuses.

    Provides a Tkinter interface to view, add, and manage credit cards
    with persistent JSON storage.
    """

    def __init__(self, root: tk.Tk) -> None:
        """
        Initialize the application.

        Args:
            root: The root Tkinter window
        """
        self.root = root
        self.root.title("Credit Card Welcome Bonus Tracker")
        self.root.geometry("900x500")

        # Load cards from storage
        self.cards: List[Card] = load_cards("cards.json")

        # Set up close handler to save before exit
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Build UI
        self.build_ui()
        self.refresh_table()

    def build_ui(self) -> None:
        """Construct the main UI layout."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights for responsiveness
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="💳 Credit Card Welcome Bonus Tracker",
            font=("Helvetica", 14, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)

        # Table section
        table_frame = ttk.Frame(main_frame)
        table_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Treeview with scrollbar
        tree_label = ttk.Label(table_frame, text="Your Cards:", font=("Helvetica", 10, "bold"))
        tree_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        # Create scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))

        # Create Treeview
        self.tree = ttk.Treeview(
            table_frame,
            columns=("Card Name", "Welcome Points", "Opened Date"),
            height=12,
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.tree.yview)

        # Define column headings and widths
        self.tree.heading("#0", text="")
        self.tree.column("#0", width=0, stretch=False)
        self.tree.heading("Card Name", text="Card Name")
        self.tree.column("Card Name", width=400, anchor=tk.W)
        self.tree.heading("Welcome Points", text="Welcome Points")
        self.tree.column("Welcome Points", width=150, anchor=tk.CENTER)
        self.tree.heading("Opened Date", text="Opened Date")
        self.tree.column("Opened Date", width=150, anchor=tk.CENTER)

        self.tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Form section
        form_frame = ttk.LabelFrame(main_frame, text="Add New Card", padding="10")
        form_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        form_frame.columnconfigure(1, weight=1)

        # Card Name
        ttk.Label(form_frame, text="Card Name:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.card_name_var = tk.StringVar()
        card_name_entry = ttk.Entry(form_frame, textvariable=self.card_name_var, width=30)
        card_name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))

        # Welcome Points
        ttk.Label(form_frame, text="Welcome Points:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.points_var = tk.StringVar()
        points_entry = ttk.Entry(form_frame, textvariable=self.points_var, width=20)
        points_entry.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(0, 10))

        # Opened Date
        ttk.Label(form_frame, text="Opened Date (YYYY-MM-DD):").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.date_var = tk.StringVar()
        date_entry = ttk.Entry(form_frame, textvariable=self.date_var, width=20)
        date_entry.grid(row=0, column=5, sticky=(tk.W, tk.E))

        # Button section
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        add_button = ttk.Button(button_frame, text="Add Card", command=self.add_card)
        add_button.pack(side=tk.LEFT, padx=(0, 5))

        delete_button = ttk.Button(button_frame, text="Delete Selected", command=self.delete_card)
        delete_button.pack(side=tk.LEFT, padx=(0, 5))

        save_button = ttk.Button(button_frame, text="Save", command=self.save_cards_to_file)
        save_button.pack(side=tk.LEFT, padx=(0, 5))

        exit_button = ttk.Button(button_frame, text="Exit", command=self.on_closing)
        exit_button.pack(side=tk.LEFT)

    def add_card(self) -> None:
        """
        Add a new card from the form inputs.
        Validates input and updates both the internal list and the table.
        """
        card_name = self.card_name_var.get().strip()
        points_str = self.points_var.get().strip()
        date_str = self.date_var.get().strip()

        # Validate card name
        if not card_name:
            messagebox.showerror("Validation Error", "Card name cannot be empty.")
            return

        # Validate welcome points
        try:
            welcome_points = int(points_str)
            if welcome_points <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Validation Error", "Welcome points must be a positive integer.")
            return

        # Validate date
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation Error", "Date must be in YYYY-MM-DD format.")
            return

        # Create and add card
        new_card: Card = {
            "card_name": card_name,
            "welcome_points": welcome_points,
            "opened_date": date_str,
        }
        self.cards.append(new_card)

        # Update table
        self.refresh_table()

        # Clear form
        self.card_name_var.set("")
        self.points_var.set("")
        self.date_var.set("")

        messagebox.showinfo("Success", f"Card '{card_name}' added successfully!")

    def refresh_table(self) -> None:
        """Update the Treeview table with current cards."""
        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert cards
        for card in self.cards:
            self.tree.insert(
                "",
                "end",
                values=(card["card_name"], card["welcome_points"], card["opened_date"])
            )

    def delete_card(self) -> None:
        """
        Delete the selected card from the table and internal list.
        Shows a confirmation dialog before deleting.
        """
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning("No Selection", "Please select a card to delete.")
            return

        # Get the index of the selected item
        item_index = self.tree.index(selected[0])

        # Confirm deletion
        card_name = self.cards[item_index]["card_name"]
        if messagebox.askyesno("Confirm Delete", f"Delete '{card_name}'?"):
            self.cards.pop(item_index)
            self.refresh_table()
            messagebox.showinfo("Deleted", f"Card '{card_name}' deleted successfully!")

    def save_cards_to_file(self) -> None:
        """Save the current card list to cards.json."""
        try:
            save_cards("cards.json", self.cards)
            messagebox.showinfo("Success", "✅ Cards saved to cards.json")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def on_closing(self) -> None:
        """Handle window close event by saving and then destroying."""
        try:
            save_cards("cards.json", self.cards)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save before closing: {e}")

        self.root.destroy()


def main() -> None:
    """Entry point for the application."""
    root = tk.Tk()
    app = CardTrackerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
