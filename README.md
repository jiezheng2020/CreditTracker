# Credit Card Welcome Bonus Tracker

A Python app to track credit cards and their welcome bonus offers. Available as a CLI, desktop GUI, or web app!

## Features

- ✅ Track multiple credit cards with welcome bonus points
- ✅ Store card name, welcome points, and date opened
- ✅ Multiple interfaces: CLI, Tkinter GUI, or web app (Streamlit)
- ✅ Persistent JSON storage (no database required)
- ✅ Input validation (date format, points must be positive)
- ✅ Friendly, readable output

## Project Structure

```
CardTracker/
├── main.py              # CLI entry point
├── app.py               # Tkinter GUI entry point
├── streamlit_app.py     # Web app entry point
├── storage.py           # Load/save logic for cards.json
├── models.py            # Card data model
├── cards.json           # Data file (created on first save)
├── requirements.txt     # Python dependencies (for web app)
└── README.md            # This file
```

## Requirements

- Python 3.8 or later
- For CLI/GUI: No external dependencies
- For web app: See `requirements.txt` (only `streamlit`)

## Installation & Running

There are three ways to run this app:

### Option 1: CLI (Command Line)

1. **Navigate** to the project folder in your terminal:

   ```bash
   cd path/to/CardTracker
   ```

2. **Run** the CLI app:

   ```bash
   python main.py
   ```

3. Use the menu to add and manage cards.

### Option 2: Desktop GUI (Tkinter)

1. **Navigate** to the project folder in your terminal:

   ```bash
   cd path/to/CardTracker
   ```

2. **Run** the GUI app:

   ```bash
   python app.py
   ```

3. Use the graphical interface to add and manage cards.

### Option 3: Web App (Streamlit) – Recommended for Sharing

#### Running Locally

1. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Navigate** to the project folder:

   ```bash
   cd path/to/CardTracker
   ```

3. **Run** the web app:

   ```bash
   streamlit run streamlit_app.py
   ```

4. Your browser will open to a local web interface (usually `http://localhost:8501`).

#### Deploying to Streamlit Community Cloud (Free)

This is the easiest way to share your app with friends via a public URL.

**Prerequisites:**

- A GitHub account
- Your CardTracker project pushed to a public GitHub repository

**Steps:**

1. **Push your project to GitHub**:

   - Ensure your GitHub repo includes:
     - `streamlit_app.py`
     - `storage.py`
     - `models.py`
     - `requirements.txt`
     - `.gitignore` (optional, but good practice)
     - `cards.json` (or let it be created on first save)

2. **Go to Streamlit Community Cloud**:

   - Visit https://share.streamlit.io/

3. **Connect your GitHub repo**:

   - Click "New app"
   - Select your GitHub repository
   - Select the branch (usually `main` or `master`)
   - Set the main file path to `streamlit_app.py`

4. **Deploy**:

   - Click "Deploy"
   - Streamlit will automatically build and deploy your app
   - You'll get a public URL (e.g., `https://cardtracker.streamlit.app`)

5. **Share the URL** with friends!

**Note on Data Persistence:**

- When deployed on Streamlit Community Cloud, the `cards.json` file is stored in the app's temporary storage.
- Data may reset if the app is redeployed or after inactivity. For permanent storage, consider upgrading to a Streamlit account or using an external database.

#### Deploying to Hugging Face Spaces (Free Alternative)

**Steps:**

1. **Create a new Space**:

   - Go to https://huggingface.co/spaces
   - Click "Create new Space"
   - Choose "Streamlit" as the template
   - Name your space and select public

2. **Push your code**:

   - Clone the Space's repository
   - Copy `streamlit_app.py`, `storage.py`, `models.py`, and `requirements.txt` to the repo
   - Commit and push:
     ```bash
     git add .
     git commit -m "Add card tracker"
     git push
     ```

3. **Done!**
   - Hugging Face will automatically deploy
   - You'll get a public URL

## Data Format

Cards are stored in `cards.json` in the following format:

```json
[
  {
    "card_name": "Chase Sapphire Preferred",
    "welcome_points": 60000,
    "opened_date": "2025-11-28"
  },
  {
    "card_name": "American Express Gold",
    "welcome_points": 75000,
    "opened_date": "2025-11-20"
  }
]
```

If `cards.json` doesn't exist, it will be created on first save.

## Input Validation

- **Card Name**: Any non-empty string
- **Welcome Points**: Positive integer (e.g., 50000)
- **Date Opened**: ISO format `YYYY-MM-DD` (e.g., 2025-11-28)

Invalid inputs will prompt you to try again.

## Building an Executable (CLI or GUI)

You can distribute the CLI or GUI as a standalone `.exe` file to friends without requiring them to install Python.

### Steps:

1. **Install PyInstaller** (if you haven't already):

   ```bash
   pip install pyinstaller
   ```

2. **Navigate** to the project folder in your terminal:

   ```bash
   cd path/to/CardTracker
   ```

3. **Build the executable** (choose one):

   **For CLI:**

   ```bash
   pyinstaller --onefile main.py
   ```

   **For GUI:**

   ```bash
   pyinstaller --onefile app.py
   ```

   This creates a `dist/` folder containing `main.exe` or `app.exe` (Windows) or `main`/`app` (macOS/Linux).

4. **Share with friends**:
   - Copy the executable from the `dist/` folder
   - When your friend runs the executable, a `cards.json` file will be created in the same directory
   - The `cards.json` file persists between runs and can be backed up or shared

### Example workflow for your friend:

```
1. Download main.exe (or app.exe)
2. Run: double-click the .exe file
3. Use the interface to add and track cards
4. Cards are saved to cards.json in the same folder
5. Share cards.json with you if needed
```

## Notes

- All interfaces (CLI, GUI, Web) share the same `cards.json` file
- Malformed or missing `cards.json` files are handled gracefully
- The web app is ideal for sharing with friends who don't have Python installed
- The CLI/GUI executables are great for offline use
- Press `Ctrl+C` in terminal to force quit (though unsaved changes will be lost in CLI)

## License

Feel free to modify and share!
