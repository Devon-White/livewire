# LiveWire SignalWire Demo

## Overview

This is a tech demo for a Flask-based SignalWire application. The project demonstrates clean code, modern Python best practices, and a clear separation between backend and frontend code. It is designed to be easy to follow and modify for learning or demonstration purposes.

## Project Structure

```
livewire/
│
├── src/
│   └── livewire/
│       ├── app.py
│       ├── routes/
│       ├── stores/
│       ├── utils/
│       └── ...
│
├── static/         # All JS, CSS, images, etc.
├── templates/      # All Jinja2 HTML templates
├── requirements.txt
├── README.md
└── ... (other config files)
```

- **Backend code** is under `src/livewire/`.
- **Frontend assets** are in `static/` and `templates/` at the project root.

## Setup Instructions

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd livewire
   ```
2. **Create a virtual environment and activate it:**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Set environment variables:**
   - `SIGNALWIRE_SPACE`: Your SignalWire space name
   - `SIGNALWIRE_PROJECT`: Your SignalWire project ID
   - `SIGNALWIRE_TOKEN`: Your SignalWire API token
   - `FLASK_SESSION_SECRET`: Secret key for session encryption (optional, generated if not set)
   - `FLASK_SESSION_LIFETIME`: Session duration in seconds (default: 3600)
   - `FLASK_DEBUG`: Enable debug mode (default: False)
   - `PORT`: Port to run the application on (default: 5000)

5. **Run the application:**
   ```sh
   cd src/livewire
   python app.py
   ```

## Demo-Specific Simplifications

This project is intentionally simplified for demo and learning purposes. **The following are NOT implemented:**

- No persistent database (in-memory stores only)
- No CSRF protection (do not use in production)
- No CORS configuration
- No HTTPS enforcement
- No production session storage (Flask's default is used)
- No caching or performance optimizations
- No role-based access control
- No database migrations
- No advanced error handling or logging

**Passwords are hashed, but this is not a production security model.**

## Clean Code & Best Practices

- All Python code uses type hints and Google-style docstrings.
- All magic numbers and strings are replaced with named constants.
- All modules and functions follow PEP 8 naming conventions.
- All API endpoints use consistent validation and error handling.
- The codebase is organized for clarity and maintainability.

## Contributing

Pull requests are welcome! Please keep code clean, well-documented, and demo-friendly.

---

**For production use, you must add proper security, persistent storage, and error handling.**
