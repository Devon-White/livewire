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

### 2024-06-10: Front-End Refactor
- Created a shared Jinja2 navbar include (`_navbar.html`) and replaced hardcoded navbars in all templates.
- Moved all agent dashboard JavaScript from `subscriber.html` to `static/js/agent_dashboard.js`.
- Removed redundant `setStatus` function; only `setDashboardStatus` is used.
- Cleaned up CSS: removed obsolete `.topbar` and `.topbar-actions` styles, ensured navbar and agent status styles are in `navbar.css`.
- Added `.demo-button-disabled` style to `core.css` for clarity and accessibility.
- All templates now use the shared navbar for DRYness and consistency.
- Improved maintainability and modularity of front-end code.

### 2024-06-11: Front-End Naming Consistency
- Renamed `static/css/pages/agent_dashboard.css` to `static/css/pages/subscribers.css` to match `subscribers.js` and `subscriber.html`.
- Updated all references in `subscriber.html` and elsewhere as needed for consistency.

### 2024-06-11: Front-End Cleanup and DRY Refactor
- Moved shared agent/dashboard styles (.agent-avatar, .agent-status, .status-dot, etc.) from navbar.css and subscribers.css to core.css for DRYness.
- Added documentation comments to all CSS files describing their purpose.
- Moved inline JS from signup.html to static/js/signup.js for maintainability.
- Updated signup.html to load the new JS file.
- Moved inline JS from index.html to static/js/index.js for consistency and maintainability.

## Multi-Layer Session-Based Authentication

The app now enforces a two-step authentication flow using session-based decorators:

1. **SignalWire Credentials Required**
   - Users must provide valid SignalWire credentials on the index page before accessing `/call`, `/login`, or `/signup`.
   - Enforced by the `@require_sw_credentials` decorator (see `utils/auth_decorators.py`).

2. **Subscriber Login Required**
   - After providing credentials, users must log in as a subscriber to access `/subscriber`.
   - Enforced by the `@require_subscriber_login` decorator (see `utils/auth_decorators.py`).

Session flags (`sw_credentials_ok`, `subscriber_ok`) are set at the appropriate points in the flow. Unauthorized access attempts are redirected with a helpful flash message.

### Guest Token Flow (2024-06-12)
- The app now uses SignalWire guest tokens for call widget authentication.
- Only SignalWire credentials are required; C2C tokens are no longer used or requested.
- The guest token is generated using the SWML handler ID as the allowed address.
- The onboarding flow is now a single step: enter credentials, the app creates/updates the SWML handler, fetches the guest token, and redirects to the call page.

See `mdc:scratchpad.md` for internal notes and integration details.

---
For more details, see `scratchpad.md` for internal notes and ongoing documentation.
