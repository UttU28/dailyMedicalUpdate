## Medical Claim Processor

Tkinter desktop app that:
- **Extracts claim data** from a structured `.txt` file into JSON (`extract.py`)
- **Optionally auto-fills a web claim** via Selenium on the Superior provider portal (`backend.py` + `pages/step0..6.py`)

## Run (Windows)

- Double-click `run_windows.bat`, or:

```bash
.\env\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Run (Ubuntu/Linux)

```bash
chmod +x run_ubuntu.sh
./run_ubuntu.sh
```

## Environment (.env)

Create a `.env` file in the project root (not committed). Common keys:

- **Chrome**
  - `CHROME_APP_PATH` (optional): full path to your Chrome executable (auto-detected if not set)
  - `CHROME_DRIVER_PATH` (optional): custom chromedriver path (otherwise uses `webdriver-manager`)
  - `BASE_CHROME_PORT` (optional, default `9222`)
- **Login (optional)**
  - `LOGIN_EMAIL`
  - `LOGIN_PASSWORD`
- **Defaults used by the steps**
  - `DEFAULT_CLIA_NUMBER`
  - `DEFAULT_PLACE_OF_SERVICE`
  - Provider defaults used in Step 5 (NPI/name/address/taxonomy, etc.)

## Build EXE (PyInstaller)

From an activated venv:

```bash
pyinstaller app.spec --clean
# pyinstaller --onefile -w app.py
```

Output: `dist/app.exe`