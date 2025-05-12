# SignalWire Demo Guide

This guide explains how the LiveWire demo application works, how to demonstrate it, and key technical details.

## Demo Walkthrough

### 1. Initial Setup (Index Page)
- Enter SignalWire credentials
- These are stored only for the session
- Used to make API calls to SignalWire

### 2. Subscriber Page
- Shows a dashboard for a subscriber
- Toggle online/offline status
- View incoming call information
- Accept/reject calls

### 3. Consumer Page
- Demonstrates calling a subscriber
- Shows call status updates
- Demonstrates how SignalWire handles call routing

### 4. SWAIG Integration
- AI-powered voice interactions
- Built using SignalWire's SWAIG platform
- Shows how to build AI voice agents

## Technical Implementation Details

### Authentication Flow
1. User enters SignalWire credentials (stored in Flask session)
2. Auth middleware checks credentials before allowing access to protected routes
3. Subscriber login uses a separate user store

### Call Handling
1. Incoming calls trigger webhooks to the `/api/swml` endpoint
2. SWML (SignalWire Markup Language) defines call flow
3. Call status updates are processed via webhooks
4. Real-time updates are shown in the UI

### Store Architecture
- The app uses in-memory stores instead of a database for simplicity
- `active_subscribers_store.py`: Manages subscriber availability
- `call_info_store.py`: Tracks active calls and their state
- `user_store.py`: Manages user authentication

### Frontend Architecture
- Vanilla JavaScript with modules
- Communicates with backend via REST APIs
- Uses Flask's Jinja2 templates for server-side rendering

## Demo Tips

1. **Preparation**
   - Have SignalWire credentials ready
   - Set up a test phone number to call from

2. **Showing Key Features**
   - Demonstrate the subscriber going online/offline
   - Show how call routing changes based on availability
   - Demonstrate SWML capabilities
   - Show the SWAIG AI interactions

3. **Code Explanation**
   - Highlight the clean separation of concerns
   - Show how the store pattern works
   - Explain the middleware for authentication
   - Demonstrate how SWML is processed

4. **Common Questions**
   - "How is call routing handled?" → Through SWML and webhooks
   - "How are updates shown in real-time?" → Polling API endpoints
   - "Can this be extended?" → Yes, the modular architecture makes it easy

## Customization Options

- Change UI theme in `static/css/core.css`
- Modify call flow in SWML files
- Add new API endpoints in `routes/api/`
- Create new pages in `routes/html/` 