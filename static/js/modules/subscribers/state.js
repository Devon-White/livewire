/**
 * subscribers/state.js
 * 
 * State management for the agent dashboard.
 * Centralizes the dashboard state and provides access functions.
 */

// Dashboard state object (single source of truth)
export const DashboardState = {
  client: null,            // SignalWire client instance
  clientListenersAttached: false, // Whether listeners have been attached to the client
  invite: null,            // Current call invite
  call: null,              // Current active call
  callAccepted: false,     // Whether the current call has been accepted
  cachedCallInfo: null,    // Cached call info from the API
  subscriberInfo: null     // Information about the current subscriber
};

// Mark listeners as attached
export function markListenersAttached() {
  DashboardState.clientListenersAttached = true;
}

// Set the invite for the current call
export function setInvite(invite) {
  DashboardState.invite = invite;
}

// Set the call for the current session
export function setCall(call) {
  DashboardState.call = call;
  DashboardState.callAccepted = true;
}

// Reset call state after a call ends
export function resetCallState() {
  DashboardState.call = null;
  DashboardState.invite = null;
  DashboardState.callAccepted = false;
}

// Update subscriber info in the state
export function updateSubscriberInfo(info) {
  DashboardState.subscriberInfo = info;
  
  // Update subscriber info table if it exists
  const table = document.getElementById('subscriberInfoTable');
  if (table && info) {
    Array.from(table.querySelectorAll('[data-field]')).forEach(td => {
      const field = td.getAttribute('data-field');
      if (info[field]) {
        td.textContent = info[field];
      } else {
        td.textContent = '-';
      }
    });
  }
} 