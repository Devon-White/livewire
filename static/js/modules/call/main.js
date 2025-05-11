/**
 * call/main.js
 * 
 * Main implementation for the call widget page.
 * Handles call widget initialization and user events.
 */

import { getWidgetConfig } from './api.js';
import { showCreateMemberModal, createWidgetHtml } from './ui.js';
import { initCreateMemberForm } from '../forms/create-member.js';

// Call state tracking
let client = null;
let call = null;
let currentCallId = null;
let userEventListener = null;

// Handle user events from the call widget
export function handleUserEvent(params) {
    console.log("User event received:", params);
    if (params.type === "create_member") {
        showCreateMemberModal(currentCallId);
        initCreateMemberForm();
    }
}

// Set up the call widget
export async function setupCallWidget() {
    const callButtonId = 'callButton'; // This matches the ID in call.html
    
    try {
        // Get configuration with guest token
        const config = await getWidgetConfig();
        
        console.log('Received widget config, setting up widget...');
        
        // Get the call button element
        const callButton = document.getElementById(callButtonId);
        if (!callButton) {
            console.error('Call button not found:', callButtonId);
            return;
        }
        
        // Create a container for the widget
        let widgetContainer = document.getElementById('widgetContainer');
        if (!widgetContainer) {
            widgetContainer = document.createElement('div');
            widgetContainer.id = 'widgetContainer';
            // Insert the container after the button
            callButton.parentNode.insertBefore(widgetContainer, callButton.nextSibling);
        }
        
        // Generate the widget HTML with the right configuration
        const widgetHtml = createWidgetHtml(callButtonId, config);
        
        // Add the widget HTML to the container
        widgetContainer.innerHTML = widgetHtml;
        
        console.log('Widget HTML inserted, looking for widget element');
        
        // Find the widget element
        const widget = document.querySelector('c2c-widget');
        if (!widget) {
            console.error('Widget element not found');
            return;
        }
        
        console.log('Widget element found, attaching event listeners');
        
        // Wait for widget to be fully initialized
        widget.addEventListener("widget.initialized", () => {
            console.log("Widget fully initialized, enabling call button");
            
            // Show the button by removing the disabled class
            // This will automatically switch from spinner to button via CSS
            callButton.classList.remove('demo-button-disabled');
        });
        
        // Attach event listeners to the widget
        widget.addEventListener("beforecall", () => {
            console.log("beforecall event - cleaning up SignalWire tokens");
            // Clean up SignalWire SAT tokens to prevent cross-widget/session issues
            ['ci-SAT', 'pt-SAT', 'as-SAT'].forEach(key => sessionStorage.removeItem(key));
        });
        
        widget.addEventListener("call.joined", ({ detail }) => {
            console.log("call.joined event with details:", detail);
            
            // Store the client and call references
            client = detail.client;
            call = detail.call;
            
            // Set the call_id from activeRTCPeerId
            if (call && call.activeRTCPeerId) {
                currentCallId = call.activeRTCPeerId;
                console.log('Current call ID set to:', currentCallId);
            } else {
                console.warn('Could not determine call ID from call object');
            }
            
            // Remove previous listener if exists (important for reconnect scenarios)
            if (userEventListener && client) {
                try {
                    client.off("user_event", userEventListener);
                } catch (e) {
                    console.warn('Error removing previous user_event listener:', e);
                }
            }
            
            // IMPORTANT: This is where we listen for user_event
            // These come from the client, not the widget element
            userEventListener = (event) => {
                console.log("user_event from client:", event);
                handleUserEvent(event);
            };
            
            client.on("user_event", userEventListener);
            console.log('Attached user_event listener to client');
        });
        
        widget.addEventListener("call.left", ({ detail }) => {
            console.log("call.left event - cleaning up resources");
            
            // Remove event listener if possible
            if (client && userEventListener) {
                try {
                    client.off("user_event", userEventListener);
                    console.log('Removed user_event listener from client');
                } catch (e) {
                    console.warn('Error removing user_event listener:', e);
                }
            }
            
            // Reset all state
            client = null;
            call = null;
            currentCallId = null;
            userEventListener = null;
        });
        
        console.log('Widget event listeners attached successfully');
        
    } catch (error) {
        console.error('Error setting up call widget:', error);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger mt-3';
        errorDiv.textContent = `Failed to initialize call widget: ${error.message}`;
        
        // Find the button and insert error after it
        const callButton = document.getElementById(callButtonId);
        if (callButton && callButton.parentNode) {
            callButton.parentNode.insertBefore(errorDiv, callButton.nextSibling);
            
            // Enable the call button in error state so it's at least visible
            callButton.classList.remove('demo-button-disabled');
        }
    }
}

// Initialize the call module when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Add a fallback timeout to show the button if widget.initialized never fires
    setTimeout(() => {
        const callButton = document.getElementById('callButton');
        
        if (callButton && callButton.classList.contains('demo-button-disabled')) {
            console.log('Fallback: Showing call button after timeout');
            callButton.classList.remove('demo-button-disabled');
        }
    }, 10000); // 10 second fallback
    
    setupCallWidget();
}); 