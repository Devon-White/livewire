# LiveWire Flask SignalWire Demo

## Overview
This project is a modular Flask application that serves as a backend for a SignalWire-powered AI receptionist/call center demo. It exposes REST and SWAIG endpoints for SignalWire AI workflows, manages dynamic public URLs via ngrok, and provides a modern, maintainable web UI.

### Key Features
- Modular Flask blueprints for HTML and API routes
- SignalWire SWAIG integration for AI-driven call flows
- Dynamic ngrok tunnel for public URL updates
- Jinja2 templates for web UI (minimized use, frontend scripts preferred)
- DRY, scalable, and human-readable codebase
- CSS organized into core, component, and page-specific files

### Directory Structure
- `app.py`: Main entry point, app setup, ngrok, blueprint registration
- `setup.py`: SignalWire handler registration/update, SWML/YAML utilities
- `routes/`: Flask blueprints for API, HTML, and SWAIG function endpoints
- `templates/`: HTML templates for web UI
- `static/`: CSS (core, components, pages)
- `scratchpad.md`: Internal notes
- `swml_id.txt`: SignalWire handler ID persistence

## Recent Changes
### 2024-06-09: Refactor of subscriber.html
- Removed duplicate function and event handler definitions
- Consolidated modal show/hide and call info update logic into helpers
- Removed unused variables and functions
- Moved inline modal styles to a `<style>` block in the head
- Cleaned up outdated comments and improved DRYness
- No change to user-facing functionality

### 2024-06-09: CSS Refactor
- Moved modal-related CSS from an inline <style> block in subscriber.html to static/css/pages/agent_dashboard.css for better separation of concerns and maintainability.

### 2024-06-09: Real-time Call Status Updates
- The call status text in the dashboard now updates in real time:
  - Shows 'Incoming call...' when a call is ringing.
  - Shows 'In call!' when a call is accepted.
  - Reverts to 'Waiting for call...' after a call ends or is hung up.
- Ensures the UI always reflects the current call state.

---
For more details, see `scratchpad.md` for internal notes and ongoing documentation.
