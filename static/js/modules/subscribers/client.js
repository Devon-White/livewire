/**
 * subscribers/client.js
 * 
 * SignalWire client interactions for the agent dashboard.
 * Handles client initialization, online/offline status, and call handling.
 */

import { DashboardState, markListenersAttached, updateSubscriberInfo } from './state.js';
import { setDashboardStatus, applyCallInfoToUI } from './ui.js';
import { showSpinner, hideSpinner, fetchAPI } from '../../utils.js';

// Initialize the client and attach event listeners
export async function createClientAndAttachListeners(host, token, handleIncomingCall) {
  try {
    DashboardState.client = await SignalWire.SignalWire({ host, token, debug: { logWsTraffic: false } });
    
    if (!DashboardState.clientListenersAttached) {
      DashboardState.client.on('call.state', (params) => {
        if (params.call_state === 'created' && params.parent && params.parent.call_id) {
          fetchAPI(`/api/call_info/${params.parent.call_id}`)
            .then(data => {
              DashboardState.cachedCallInfo = data;
              applyCallInfoToUI(data, DashboardState.callAccepted);
            })
            .catch(() => {
              DashboardState.cachedCallInfo = null;
              applyCallInfoToUI(null, DashboardState.callAccepted);
            });
        }
        // Hide modal if call ended
        if (params.call_state === 'ended') {
          try {
            const bootstrap = window.bootstrap;
            if (bootstrap) {
              const modal = bootstrap.Modal.getInstance(document.getElementById('incomingCallModal'));
              if (modal) modal.hide();
            }
          } catch (e) {
            console.error('Error hiding modal:', e);
          }
        }
      });
      markListenersAttached();
    }
    
    try {
      // Get and log subscriber info
      const subscriberInfo = await DashboardState.client.getSubscriberInfo();
      console.log('Retrieved subscriber info:', subscriberInfo);
      
      // Ensure we have some basic data if fields are missing
      const enhancedInfo = {
        first_name: 'Demo',
        last_name: 'Agent',
        email: 'agent@example.com',
        id: subscriberInfo?.id || 'unknown',
        ...subscriberInfo // This will overwrite defaults with actual values if present
      };
      
      // Update state and UI
      updateSubscriberInfo(enhancedInfo);
      return enhancedInfo;
    } catch (subscriberError) {
      console.error('Error getting subscriber info:', subscriberError);
      // Provide minimal fallback data
      const fallbackInfo = {
        first_name: 'Demo',
        last_name: 'Agent',
        email: 'agent@example.com',
        id: 'unknown'
      };
      updateSubscriberInfo(fallbackInfo);
      return fallbackInfo;
    }
  } catch (error) {
    console.error('Error creating client:', error);
    throw error;
  }
}

// Go online and handle incoming calls
export async function goOnline(host, token, handleIncomingCall, spinner) {
  setDashboardStatus('connecting');
  showSpinner(spinner);
  
  let triedNewToken = false;
  let attempt = 0;
  const maxAttempts = 3;
  const retryDelay = 1500;
  
  while (attempt < maxAttempts) {
    try {
      if (!DashboardState.client) {
        // If no client, fetch token and create
        try {
          const data = await fetchAPI('/api/create_sat', { 
            method: 'POST',
            body: JSON.stringify({})
          });
          
          // Token is directly available in the returned data
          token = data.token;
          
          await createClientAndAttachListeners(host, token, handleIncomingCall);
        } catch (error) {
          console.error('Error fetching token:', error);
          throw error;
        }
      }
      
      await DashboardState.client.online({ incomingCallHandlers: { all: handleIncomingCall } });
      return true;
    } catch (err) {
      console.error('Error going online:', err);
      
      // If token error and we haven't tried a new token yet
      if (!triedNewToken && (err.message?.includes('token') || err.message?.includes('401'))) {
        triedNewToken = true;
        try {
          const data = await fetchAPI('/api/create_sat', { 
            method: 'POST',
            body: JSON.stringify({})
          });
          
          token = data.token;
          await createClientAndAttachListeners(host, token, handleIncomingCall);
          continue;
        } catch (tokenErr) {
          console.error('Failed to get new token:', tokenErr);
        }
      }
      
      // Wait before retrying
      await new Promise(res => setTimeout(res, retryDelay));
      attempt++;
    }
  }
  
  return false;
}

// Go offline
export async function goOffline() {
  if (DashboardState.client && typeof DashboardState.client.offline === 'function') {
    try {
      await DashboardState.client.offline();
      return true;
    } catch (error) {
      console.error('Error going offline:', error);
      return false;
    }
  }
  return false;
}

// Handle call acceptance
export async function acceptCall() {
  if (!DashboardState.invite) return null;
  
  try {
    const call = await DashboardState.invite.accept({ audio: true, video: false });
    return call;
  } catch (error) {
    console.error('Error accepting call:', error);
    throw error;
  }
}

// Handle call rejection
export async function rejectCall() {
  if (DashboardState.invite) {
    try { 
      await DashboardState.invite.reject(); 
      return true;
    } catch (error) { 
      console.error('Failed to reject call:', error); 
      return false;
    }
  }
  return false;
}

// Handle call hangup
export async function hangupCall() {
  if (DashboardState.call && typeof DashboardState.call.hangup === 'function') {
    try { 
      await DashboardState.call.hangup(); 
      return true;
    } catch (error) {
      console.error('Failed to hang up call:', error);
      return false;
    }
  }
  return false;
}

// Clean up resources before page unload
export function cleanupBeforeUnload() {
  // Hangup any active call
  if (DashboardState.call && typeof DashboardState.call.hangup === 'function') {
    try { DashboardState.call.hangup(); } catch (err) {}
  }
  
  // Disconnect SignalWire client
  if (DashboardState.client && typeof DashboardState.client.disconnect === 'function') {
    try { DashboardState.client.disconnect(); } catch (err) {}
  }
  
  // Notify backend that subscriber is going offline
  const subscriberId = DashboardState.subscriberInfo && DashboardState.subscriberInfo.id;
  if (subscriberId) {
    // Using fetch directly with keepalive for page unload scenario
    // fetchAPI doesn't work well with keepalive for page unload
    fetch(`/api/subscriber_offline/${subscriberId}`, {
      method: 'POST',
      keepalive: true, // This allows the request to complete even after the page is unloaded
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    }).catch(err => console.error('Error marking subscriber offline:', err));
  }
} 