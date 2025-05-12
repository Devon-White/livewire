# LiveWire - SignalWire Demo Application

## Overview

LiveWire is a demo application showcasing [SignalWire](https://signalwire.com/) capabilities for voice, messaging, and AI integrations. The project is structured to be easy to understand and modify, following modern Python best practices.


## 🚀 Quick Start (Replit)

1. **Fork this Replit**: Click the "Fork" button to create your own copy
2. **Set up environment variables** in the Replit Secrets panel:
   - `SIGNALWIRE_SPACE`: Your SignalWire space name
   - `SIGNALWIRE_PROJECT`: Your SignalWire project ID
   - `SIGNALWIRE_TOKEN`: Your SignalWire API token
   - `NGROK_AUTHTOKEN`: Your ngrok authtoken (optional, but recommended)
3. **Click Run**: The application will automatically install dependencies and start

## 🧩 Project Structure

```
livewire/
│
├── src/livewire/         # Backend code
│   ├── app.py            # Main application entry point
│   ├── routes/           # API and HTML endpoints
│   │   ├── api/          # Backend API endpoints
│   │   ├── html/         # Page routes
│   │   └── swaig_functions/ # SignalWire AI functions
│   ├── stores/           # In-memory data management
│   └── utils/            # Helper functions
│
├── static/               # Frontend assets
│   ├── css/              # Styles
│   └── js/               # Client-side code
│      └── modules/       # JavaScript modules by feature
│
├── templates/            # HTML templates (Jinja2)
│
├── .replit               # Replit configuration
├── Makefile              # Build and run commands
└── requirements.txt      # Python dependencies
```

## 📖 Feature Documentation

### Voice Calling
- Handles inbound/outbound calls via SignalWire
- Uses SWML (SignalWire Markup Language) for call flow control
- Provides call monitoring and status updates

### Subscriber Management
- Demo user authentication system
- Subscriber status tracking
- Call routing based on subscriber availability

### AI Integration
- Uses SignalWire SWAIG for AI-powered voice experiences
- Demonstrates AI agent capabilities
- Shows practical usage patterns for the SignalWire AI platform

## 🛠 Development

### Local Setup
1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment: 
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `make install`
5. Set up environment variables (see .env.example)
6. Run the application: `make start`

### Makefile Commands
- `make install`: Install dependencies
- `make start`: Run the application
- `make lint`: Check code style
- `make format`: Format code
- `make clean`: Clean up temporary files

## 📝 Notes

This is a tech demo only and includes intentional simplifications:
- Uses in-memory storage instead of a database
- Limited error handling and security features
- Simplified authentication flow

## 🔗 Resources

- [SignalWire Documentation](https://developer.signalwire.com/)
- [SWML Documentation](https://developer.signalwire.com/swml)
- [SWAIG Documentation](https://developer.signalwire.com/swml/methods/ai/swaig) 