/**
 * subscribers/main.js
 * 
 * Main implementation for the subscribers module.
 * Orchestrates the UI, state, and client interactions for the agent dashboard.
 */

import { DashboardState, setInvite, setCall, resetCallState } from './state.js';
import { 
  setDashboardStatus, 
  showModal, 
  hideModal, 
  updateSubscriberUI, 
  applyCallInfoToUI, 
  clearCallInfo,
  createGoOnlineSpinner,
  resetAfterCallEnd
} from './ui.js';
import { 
  createClientAndAttachListeners, 
  goOnline, 
  goOffline, 
  acceptCall as clientAcceptCall,
  rejectCall as clientRejectCall,
  hangupCall as clientHangupCall,
  cleanupBeforeUnload
} from './client.js';
import { hideSpinner } from '../../utils.js';

// Clean up SignalWire SAT tokens to prevent cross-widget/session issues
['ci-SAT', 'pt-SAT', 'as-SAT'].forEach(key => sessionStorage.removeItem(key));

// DOM elements
const callStatus = document.getElementById('callStatus');
const hangupCallBtn = document.getElementById('hangupCallBtn');
const callInfoDiv = document.getElementById('callInfo');
const goOnlineBtn = document.getElementById('goOnlineBtn');
const goOfflineBtn = document.getElementById('goOfflineBtn');
const tokenInput = document.getElementById('token');
const modalAcceptCallBtn = document.getElementById('modalAcceptCallBtn');
const modalRejectCallBtn = document.getElementById('modalRejectCallBtn');
const showSubscriberInfoBtn = document.getElementById('showSubscriberInfo');

// Create and add spinner
const goOnlineSpinner = createGoOnlineSpinner();
if (goOnlineBtn && goOnlineBtn.parentNode) {
  goOnlineBtn.parentNode.insertBefore(goOnlineSpinner, goOnlineBtn.nextSibling);
}

// Entry point - initialize the dashboard
export function initDashboard() {
  setDashboardStatus('offline');
  
  // Wire up buttons
  if (goOnlineBtn) goOnlineBtn.onclick = handleGoOnline;
  if (goOfflineBtn) goOfflineBtn.onclick = handleGoOffline;
  if (modalAcceptCallBtn) modalAcceptCallBtn.onclick = handleAcceptCall;
  if (modalRejectCallBtn) modalRejectCallBtn.onclick = handleRejectCall;
  if (hangupCallBtn) hangupCallBtn.onclick = handleHangupCall;
  if (showSubscriberInfoBtn) {
    showSubscriberInfoBtn.onclick = function(e) {
      e.preventDefault();
      showModal('subscriberInfoModal');
    };
  }
  
  // Set up beforeunload handler
  window.addEventListener('beforeunload', cleanupBeforeUnload);
}

// Handler: Go online button click
export async function handleGoOnline() {
  goOnlineBtn.disabled = true;
  goOnlineBtn.classList.add('hidden');
  
  let token = tokenInput ? tokenInput.value : '';
  const host = document.getElementById('host')?.value;
  
  const onlineSuccess = await goOnline(host, token, handleIncomingCall, goOnlineSpinner);
  
  hideSpinner(goOnlineSpinner);
  if (onlineSuccess) {
    setDashboardStatus('online');
    if (goOfflineBtn) goOfflineBtn.classList.remove('hidden');
    goOnlineBtn.classList.add('hidden');
  } else {
    setDashboardStatus('failed');
    goOnlineBtn.disabled = false;
    goOnlineBtn.classList.remove('hidden');
  }
}

// Handler: Go offline button click
export async function handleGoOffline() {
  await goOffline();
  setDashboardStatus('offline');
  goOfflineBtn.classList.add('hidden');
  goOnlineBtn.classList.remove('hidden');
  goOnlineBtn.disabled = false;
}

// Handler: Incoming call notification
export function handleIncomingCall(notification) {
  setInvite(notification.invite);
  
  let callerIdName = notification.invite.details.caller_id_name;
  let callerIdNumber = notification.invite.details.caller_id_number;
  let mainCaller = (callerIdName && callerIdName !== '_undef_') ? callerIdName : (callerIdNumber && callerIdNumber !== '_undef_') ? callerIdNumber : 'Unknown Caller';
  
  const incomingCallerName = document.getElementById('incomingCallerName');
  if (incomingCallerName) incomingCallerName.textContent = mainCaller;
  
  const incomingCallerSummary = document.getElementById('incomingCallerSummary');
  if (incomingCallerSummary) incomingCallerSummary.textContent = '';
  
  showModal('incomingCallModal');
  if (hangupCallBtn) hangupCallBtn.classList.add('hidden');
  
  DashboardState.callAccepted = false;
  clearCallInfo(); // Hide dashboard info until accepted
  setDashboardStatus('incoming');
}

// Handler: Accept call button click
export async function handleAcceptCall() {
  try {
    const call = await clientAcceptCall();
    if (!call) return;
    
    setCall(call);
    setDashboardStatus('in-call');
    
    if (hangupCallBtn) {
      hangupCallBtn.classList.remove('hidden');
      hangupCallBtn.disabled = false;
    }
    
    applyCallInfoToUI(DashboardState.cachedCallInfo, true); // Now show call info in dashboard
    hideModal('incomingCallModal');
    
    call.on('destroy', () => {
      resetCallState();
      resetAfterCallEnd(hangupCallBtn);
    });
  } catch (e) {
    alert('Failed to accept call: ' + e.message);
  }
}

// Handler: Reject call button click
export async function handleRejectCall() {
  await clientRejectCall();
  hideModal('incomingCallModal');
  
  DashboardState.callAccepted = false;
  clearCallInfo();
  setDashboardStatus('online');
}

// Handler: Hangup call button click
export async function handleHangupCall() {
  await clientHangupCall();
  resetCallState();
  resetAfterCallEnd(hangupCallBtn);
}

// Initialize the dashboard when the DOM is ready
document.addEventListener('DOMContentLoaded', initDashboard); 