# LiveWire Flask SignalWire Demo

## Overview
This project is a modular Flask application that serves as a backend for a SignalWire-powered AI receptionist/call center demo. It exposes REST and SWAIG endpoints for SignalWire AI workflows, manages dynamic public URLs via ngrok, and provides a modern, maintainable web UI.

## Quickstart

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd livewire
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set environment variables:**
   Create a `.env` file in the project root with the following (replace with your SignalWire credentials):
   ```env
   SIGNALWIRE_SPACE=your-space
   SIGNALWIRE_PROJECT=your-project-id
   SIGNALWIRE_TOKEN=your-api-token
   ```
5. **Run the app:**
   ```bash
   python app.py
   ```
   The app will start on `localhost:5000` and expose a public URL via ngrok (see console output).

6. **Access the demo:**
   - Open the public ngrok URL in your browser.
   - Enter your SignalWire credentials on the landing page.
   - Log in as a subscriber or use the call widget to interact with the AI agent.

## System Architecture

### Overview
The app follows a modular architecture with clear separation of concerns:

1. **Flask Backend** - Serves HTML pages, REST APIs, and SWAIG function endpoints
2. **SignalWire Integration** - Manages SWML handlers, SWAIG functions, and guest tokens
3. **Ngrok Tunnel** - Creates public URLs accessible to SignalWire services
4. **Frontend UI** - Provides user interfaces for callers and subscribers

### Major Components

#### Backend
- **Flask Blueprints** - Modular route organization (HTML, API, SWAIG)
- **In-Memory Stores** - Track users, calls, customers, active subscribers
- **Authentication** - Session-based with custom decorators
- **SWML Handling** - Dynamic generation/updating of SWML handlers
- **SWAIG Functions** - Auto-registered endpoints for AI interaction

#### Frontend
- **Call Widget** - Powered by SignalWire guest tokens
- **Subscriber Dashboard** - Real-time call notifications and management
- **Modular CSS/JS** - Organized into core, components, and pages
- **Form Handling** - Member creation, sign-up, and sign-in flows

#### Data Flow
1. Users authenticate with SignalWire credentials
2. Ngrok exposes the app to SignalWire services
3. SWML handler routes calls to the app
4. AI agent interacts with callers according to main_swml.yaml
5. SWAIG functions handle member verification and data management
6. Subscribers receive and manage calls in real-time

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
- `static/`: CSS (core, components, pages) and JS files
- `stores/`: In-memory data stores
- `utils/`: Helper utilities for auth, sessions, and SWML handling
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

### 2024-06-12: UI/UX Improvements
- Added a loading spinner/indicator to the login form that matches the current theme. Login is now handled via AJAX for better UX and error handling.
- Styled the call button on the Calls page to match the theme and added a phone icon (SVG, Bootstrap style).
- Added a reusable spinner style to core.css for consistent loading indicators.
- Added a themed spinner to the subscribers dashboard when connecting to the client (goOnlineBtn click). Spinner is shown next to the button and hidden on completion/failure.
- Added a themed spinner to the index page (SignalWire credentials form) during async submission, matching the login form's UX.

### 2024-06-12: Fix for Bootstrap Modal Error in call.js
- Added Bootstrap JS CDN include to call.html to ensure `bootstrap` global is available for modal handling in call.js.
- Fixes ReferenceError: bootstrap is not defined when showing the Create Member modal from the call widget.

### 2024-06-12: create_member API logic
- The /api/create_member endpoint now:
  - Extracts form values from the POST request.
  - Retrieves the current call_id from the form, session, or call_info_store.
  - Assigns a unique member_id to each new member and stores them in a global customer_store.
  - Formats a prompt listing all form values as key-value pairs.
  - Injects the prompt to the agent using the SignalWire REST API (calling.ai_message).
  - Unholds the agent using the SignalWire REST API (calling.ai_unhold).
  - Handles errors and returns appropriate status codes.
- This enables the AI to receive the user's form input and resume the call flow.
- The customer_store is used for member verification in the verify_customer_id SWAIG function, so new members can be verified on future calls.

### 2024-06-13: Track Online Subscribers & Address Abstraction
- When a subscriber logs in, their SignalWire address is fetched and stored in a new `active_subscribers` store.
- Address-fetching logic is now abstracted into a utility for DRYness and maintainability.
- This enables tracking which subscribers are online and their addresses for future support transfer features.

### 2024-06-14: JavaScript Modularization

- Refactored JavaScript codebase into a modular structure for better maintainability.
- Created directory structure in `static/js/modules/` with dedicated subdirectories for subscribers, call, and forms functionality.
- Split large JS files into smaller, focused modules with clear responsibilities:
  - UI components: Handle DOM manipulation and visual elements
  - State management: Centralize application state
  - API/client interactions: Handle external service communication
- Created shared form validation module to eliminate duplication between signup and member creation forms.
- Added entry point files for each HTML template for cleaner imports.
- Benefits include improved code organization, reduced duplication, better separation of concerns, and easier maintenance.
- See `scratchpad.md` for detailed documentation of the modularization approach.

### 2024-06-14: JavaScript Module Pattern Improvement

- Enhanced the module pattern by implementing "barrel exports" for a cleaner API.
- Each module now has:
  - An `index.js` that re-exports functionality from sub-modules (the public API)
  - A `main.js` that contains core implementation logic
  - Specialized sub-modules for UI, state management, etc.
- Benefits:
  - Creates a clean, well-defined public API for each module
  - Makes imports simpler and more consistent
  - Isolates implementation details from the public interface
  - Improves code organization and maintainability
- This pattern makes the codebase more resilient to changes and better suited for future expansion.
- See `scratchpad.md` for more details on the barrel exports pattern.

### 2024-06-14: JavaScript Module Architecture Simplification

- Further streamlined the module architecture by:
  - Removing unnecessary intermediate entry point files (`*-main.js`)
  - Having HTML templates directly import from module index files
  - Eliminating a layer of abstraction between templates and modules
- This simplification makes the codebase even more maintainable by:
  - Making dependencies explicit and direct
  - Reducing the number of files to maintain
  - Creating a more intuitive architecture
- Also reduces the need to track changes across multiple files when modifying behavior.

### 2024-06-15: Fixed SWAIG Function Integration

- Fixed integration between the create member form and the SWAIG `send_user_info` function:
  - Added missing `summary` field to the create member form (required by the SWAIG function)
  - Enhanced backend API to handle both JSON and form data submissions
  - Updated form validation to require all fields needed by the AI agent
- Improved backend flexibility by enabling both JSON and form-encoded API submissions
- Ensured proper data flow from user input to the AI agent via the SWAIG function

### 2024-06-15: API Format Standardization

- Standardized all API endpoints to exclusively use JSON format:
  - Updated all endpoints to explicitly require JSON content-type
  - Added consistent error handling for non-JSON requests (400 Bad Request)
  - Standardized 6 API endpoints including `/api/create_member`, `/api/widget_config`, etc.
- Updated all client-side API calls to:
  - Use `'Content-Type': 'application/json'` headers
  - Send data with `JSON.stringify()`
  - Maintain consistent request/response patterns
- Benefits include:
  - Consistent, predictable API behavior
  - Clearer expectations for API consumers
  - Simplified server-side validation
  - Improved codebase maintainability
- See `scratchpad.md` for complete implementation details

### 2024-06-15: Standardized Client-Side API Calls

- Refactored all client-side API calls to use the shared `fetchAPI` helper function:
  - Updated modules for subscribers, forms, call widget, and index page
  - Centralized error handling and response format verification
  - Removed duplicated API call boilerplate across the codebase
- The `fetchAPI` helper automatically:
  - Sets proper JSON content-type headers
  - Processes JSON responses consistently
  - Checks for API success status and error messages
  - Returns the data portion directly for cleaner usage
- Benefits include:
  - More concise and readable API call code
  - Consistent error handling and user feedback
  - Better propagation of error messages to the UI
  - Easier maintenance and future updates
- Maintained specialized handling for page unload scenarios

### 2024-06-15: Removed Unused JavaScript Functions

- Cleaned up the codebase by removing 7 unused functions and imports:
  - Eliminated redundant state management functions in the subscribers module
  - Removed unused modal and form utility functions
  - Deleted unused utility function in utils.js
  - Removed unnecessary imports in call module
  - Updated related imports to maintain codebase integrity
- This cleanup:
  - Reduces code size and complexity
  - Improves maintainability by eliminating dead code
  - Removes potential confusion from duplicate implementations
  - Makes future refactoring more straightforward
- No impact on existing functionality as these functions were not being called

### 2024-06-16: Fixed Call Widget Implementation

- Fixed critical SignalWire Call Widget integration:
  - Corrected fundamental event handling approach:
    - `user_event` handler attached to SignalWire client (not widget element)
    - Proper initialization sequence for widget setup
    - Appropriate event lifecycle management
  - Implemented correct reference handling:
    - Direct reference tracking for client and call objects
    - Proper cleanup on call termination
  - Added comprehensive logging for debugging
- Fixed empty subscriber info with fallback data and defensive programming
- These changes ensure the critical call functionality works correctly
- Simplified code structure for better maintainability and debugging

### 2024-06-17: JavaScript Architecture Cleanup

- Performed comprehensive code review and optimization:
  - Verified removal of unused or duplicate functions across modules
  - Simplified event handler implementations for better readability
  - Preserved critical functions used across modules (like showMemberIdModal)
- Validated proper module structure:
  - Confirmed consistent use of barrel exports pattern
  - Verified direct template-to-module imports
  - Ensured clean separation of concerns in all modules
- Enhanced call widget implementation:
  - Implemented robust event listener management with explicit reference tracking
  - Added proper cleanup to prevent memory leaks
  - Enhanced error handling for better resilience
  - Improved logging for easier debugging
  - Added support for reconnect scenarios
  - Ensured complete state reset on call termination
- These changes further streamline the codebase without altering functionality

### 2024-06-17: Session Management Refactoring

- Enhanced session management with a more consistent, centralized approach:
  - Added constants for all session keys to prevent typos and improve maintainability
  - Created utility functions for all session operations (`set_swml_handler_info`, `set_current_call_id`)
  - Removed direct session manipulation from route handlers in favor of utility functions
  - Added better logging for session operations
  - Updated core routes to use the improved session utilities
- Benefits include:
  - More consistent session handling across the application
  - Reduced risk of bugs from mistyped session keys
  - Improved maintainability with centralized session management
  - Better debugging capabilities with enhanced logging
  - DRYer code with reusable session manipulation functions

### 2024-06-17: API Error Handling and SignalWire API Abstraction

- **API Error Handling Consistency**:
  - Added a `validate_json_request` decorator in `utils/api_utils.py` to standardize JSON validation
  - Decorator validates both JSON content type and required fields
  - Applied to all API endpoints to ensure consistent error handling
  - Eliminated duplicate validation code across endpoints
  - Improved error messages with field validation
  - Standardized error response format and status codes

- **SignalWire API Abstraction**:
  - Created a dedicated `SignalWireClient` class in `utils/signalwire_client.py` 
  - Centralized all SignalWire API interaction logic
  - Implemented robust error handling with custom `SignalWireAPIError` exception
  - Added methods for common operations (SWML handlers, call control, guest tokens)
  - Updated all endpoints to use the client instead of direct API calls
  - Reduced code duplication and improved consistency
  - Better logging and debugging of API interactions
  - Helper methods for common operations like destination extraction
  - Consolidated subscriber address fetching functionality from utility functions
  - Expanded client to handle subscriber token creation and management
  - Removed redundant utility functions that have been replaced by the client
  - Simplified signup flow with proper error handling

These changes significantly improve code maintainability, readability, and error handling across the application while reducing duplication and ensuring consistent API interactions.

### 2024-06-17: Fixed Guest Token API Endpoint Path

- Fixed a critical bug in the SignalWireClient:
  - The guest token API endpoint was incorrectly set to `fabric/resources/guest_tokens`
  - Corrected to the proper path: `fabric/guests/tokens`
  - This resolves 404 errors when attempting to generate guest tokens
  - Verified other API endpoint paths are correctly configured
- This fix ensures the call widget can properly authenticate with SignalWire using guest tokens

### 2024-06-17: Enhanced Member Creation Workflow

- Added a new convenience method to the SignalWireClient:
  - `notify_ai_about_new_member` combines message sending and agent unholding in one method
  - Simplified the create_member endpoint code by replacing separate API calls
  - Improves readability and maintainability of member creation workflow
- This enhancement follows the principle of creating meaningful, higher-level abstractions

### 2024-06-17: Implemented Session-Managed SignalWireClient

- Added session management for the SignalWireClient:
  - Added `get_rest_client()` utility function that retrieves or creates a client as needed
  - Client is initialized when credentials are set and stored in the session
  - All endpoints now use the shared client from the session
  - Removed redundant client creation code from endpoints
- Benefits include:
  - Improved efficiency by eliminating repeated client creation
  - Reduced credential validation code in endpoints
  - Simplified API endpoint implementations
  - Consistent client configuration across all API calls
  - Better state management across requests

### 2024-06-18: API Client Retry Mechanism

- Enhanced the SignalWireClient with robust retry logic:
  - Added automatic retries for transient errors (429, 500, 502, 503, 504)
  - Implemented exponential backoff for retries
  - Added configurable retry count and delay settings
  - Improved error classification and logging
  - More detailed error information with retryable flag
- This enhancement improves application reliability when the SignalWire API experiences temporary issues.

### 2024-06-18: Enhanced API Validation

- Expanded the API validation decorator with more features:
  - Added support for field type validation
  - Added custom validators for specific fields
  - Improved error messages with detailed validation errors
  - Added built-in validators for common fields (email, phone)
  - Enhanced error response format with detailed error information
- These improvements help catch API input errors earlier and provide better feedback to API consumers.

### 2024-06-18: Session Management Improvements

- Enhanced session management with environment variable configuration:
  - Session secret can now be set via the `FLASK_SESSION_SECRET` environment variable
  - Session lifetime can be configured via `FLASK_SESSION_LIFETIME`
  - Debug mode can be toggled via `FLASK_DEBUG`
  - Port can be configured via `PORT`
- This provides more flexibility for deployment while maintaining backward compatibility.

### 2024-06-24: Improved Call Button Loading State

- Enhanced the call button with an integrated loading state:
  - Implemented a unified button component that contains both call and loading states
  - Used CSS selectors and the `.demo-button-disabled` class to toggle between states
  - Made the loading state not look like a button (transparent background, no border)
  - Displayed a spinner with "Initializing widget..." text during initialization
  - Added clear visual distinction between loading and active states
  - Simplified JavaScript by removing MutationObserver code
  - Kept fallback timeout mechanism for reliability
  - Ensured button becomes visible even in error states

- Benefits:
  - More intuitive user experience with clear loading feedback
  - Simplified code with CSS-driven state management
  - Better semantics with a single button element
  - Reduced JavaScript complexity for higher reliability
  - Consistent appearance across different initialization scenarios

This implementation follows modern frontend practices by using CSS for presentation and minimal JavaScript for behavior, creating a clean separation of concerns and improved maintainability.

### 2024-06-24: Enhanced Member ID Modal with Copy Button

- Added a copy button to the Member ID modal:
  - Allows users to copy their Member ID to clipboard with a single click
  - Provides visual feedback by changing button text from "Copy" to "Copied"
  - Automatically reverts back to "Copy" after 2 seconds
  - Uses familiar clipboard icon from Bootstrap Icons
  - Styled to match the modal's design language

- Benefits:
  - Improves user experience by eliminating manual copying
  - Prevents transcription errors when users need to enter their ID later
  - Follows modern UX conventions for copyable content
  - Enhances usability of the member creation flow

## Environment Variables

The application uses the following environment variables for configuration:

- `SIGNALWIRE_SPACE`: Your SignalWire space name
- `SIGNALWIRE_PROJECT`: Your SignalWire project ID
- `SIGNALWIRE_TOKEN`: Your SignalWire API token
- `FLASK_SESSION_SECRET`: Secret key for session encryption (generated if not set)
- `FLASK_SESSION_LIFETIME`: Session duration in seconds (default: 3600)
- `FLASK_DEBUG`: Enable debug mode (default: False)
- `PORT`: Port to run the application on (default: 5000)

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

## Features

- **Create Member Modal**: When a `create_member` user event is received (e.g., from the call widget), a modal with the signup form is shown, overlaying the call widget. The form POSTs to `/api/create_member`.
- **/api/create_member Endpoint**: New API endpoint that currently returns an empty 200 response. Intended for member creation logic in the future.

## Code Refactoring Roadmap (2024-06-25)

The following refactoring opportunities have been identified to improve code quality, maintainability, and scalability:

### 1. CSS Organization and Redundancy Removal
- Move all inline styles from HTML templates to appropriate CSS files
- Create shared modal component styles in `core.css` for reuse across pages
- Consolidate duplicate styles between components

### 2. JavaScript Architecture Refinement
- Further consolidate related functionality across module files
- Ensure consistent patterns throughout JavaScript modules
- Consider implementing a state machine pattern for call handling

### 3. Session Management Enhancement
- Refactor `session_utils.py` to use a more object-oriented approach
- Standardize and simplify logging throughout session operations
- Implement a decorator pattern for common session operations

### 4. Authentication Streamlining
- Consolidate authentication logic into Flask decorators for all protected routes
- Implement a more unified approach to access control

### 5. Template Modularization
- Use Jinja2 macros or includes for common UI components like modals
- Create a component-based approach to template organization

### 6. Error Handling Standardization
- Implement a consistent error handling strategy across the application
- Standardize error messages and user feedback

### 7. Store Operations Rework
- Consider an object-oriented approach for stores to better encapsulate related functionality
- Implement a more unified API for store operations

### 8. Route Organization Simplification
- Consolidate related endpoints with minimal logic
- Consider a feature-based rather than technology-based organization

---
For more details, see `scratchpad.md` for internal notes and ongoing documentation.
