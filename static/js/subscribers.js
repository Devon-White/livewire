/*
 * subscribers.js
 *
 * JavaScript for the Agent Dashboard (subscriber.html).
 * Handles SignalWire client connection, call state, UI updates, and modals for the agent dashboard.
 * Modularized for maintainability and future scalability. Uses a simple state object for dashboard state.
 */

import { showSpinner, hideSpinner } from './utils.js';

// Clean up SignalWire SAT tokens to prevent cross-widget/session issues
['ci-SAT', 'pt-SAT', 'as-SAT'].forEach(key => sessionStorage.removeItem(key));

const DashboardState = {
  client: null,
  clientListenersAttached: false,
  invite: null,
  call: null,
  currentCallId: null,
  cachedCallInfo: null,
  subscriberInfo: null,
  callAccepted: false
};

const callStatus = document.getElementById('callStatus');
const hangupCallBtn = document.getElementById('hangupCallBtn');
const callInfoDiv = document.getElementById('callInfo');
const goOnlineBtn = document.getElementById('goOnlineBtn');
const goOfflineBtn = document.getElementById('goOfflineBtn');
const tokenInput = document.getElementById('token');
const modalAcceptCallBtn = document.getElementById('modalAcceptCallBtn');
const modalRejectCallBtn = document.getElementById('modalRejectCallBtn');

// Helper: Update subscriber info in UI
function updateSubscriberUI(info) {
  const avatar = document.querySelector('.agent-avatar');
  if (avatar) {
    avatar.textContent = (info.first_name && info.first_name[0]) || (info.email && info.email[0]) || 'SW';
  }
  const table = document.getElementById('subscriberInfoTable');
  if (table) {
    ["email","first_name","last_name","display_name","job_title","time_zone","country","region","company_name","id"].forEach(field => {
      const cell = table.querySelector(`[data-field="${field}"]`);
      if (cell) cell.textContent = info[field] || '';
    });
  }
}

// Helper: Show/hide modal using Bootstrap API
function showModal(id) {
  var modal = bootstrap.Modal.getOrCreateInstance(document.getElementById(id));
  modal.show();
}
function hideModal(id) {
  var modal = bootstrap.Modal.getOrCreateInstance(document.getElementById(id));
  modal.hide();
}

// Helper: Format caller info for modal/dashboard
function formatCallerInfo(data, labelName = 'Name', labelSummary = 'Summary') {
  let html = '';
  if (data && (data.first_name || data.last_name || data.summary)) {
    if (data.first_name || data.last_name) {
      html += `<b>${labelName}:</b> ${[data.first_name, data.last_name].filter(Boolean).join(' ')}<br>`;
    }
    if (data.summary) {
      html += `<b>${labelSummary}:</b> ${data.summary}`;
    }
  } else {
    html = '<i>No info provided.</i>';
  }
  return html;
}

// Helper: Set call info in both modal and dashboard
function applyCallInfoToUI(data) {
  const incomingSummary = document.getElementById('incomingCallerSummary');
  if (incomingSummary) incomingSummary.innerHTML = formatCallerInfo(data, 'Name', 'Summary');
  const callInfoArea = document.getElementById('callInfo');
  if (callInfoArea) {
    callInfoArea.innerHTML = formatCallerInfo(data, 'Caller', 'Summary');
    if (DashboardState.callAccepted) {
      callInfoArea.classList.remove('hidden');
    } else {
      callInfoArea.classList.add('hidden');
    }
  }
}

// Helper: Set dashboard status dot, text, and call status text
function setDashboardStatus(state) {
  const dot = document.getElementById('statusDot');
  const text = document.getElementById('statusText');
  if (!dot || !text || !callStatus) return;
  switch (state) {
    case 'connecting':
      dot.className = 'status-dot status-connecting';
      text.textContent = 'Connecting';
      callStatus.textContent = 'Connecting...';
      break;
    case 'online':
      dot.className = 'status-dot status-online';
      text.textContent = 'Online';
      callStatus.textContent = 'Waiting for call...';
      break;
    case 'incoming':
      dot.className = 'status-dot status-online';
      text.textContent = 'Online';
      callStatus.textContent = 'Incoming call...';
      break;
    case 'in-call':
      dot.className = 'status-dot status-in-call';
      text.textContent = 'In Call';
      callStatus.textContent = 'In call!';
      break;
    case 'offline':
      dot.className = 'status-dot status-offline';
      text.textContent = 'Offline';
      callStatus.textContent = 'Offline. Not receiving calls.';
      break;
    case 'failed':
      dot.className = 'status-dot status-offline';
      text.textContent = 'Offline';
      callStatus.textContent = 'Failed to connect.';
      break;
    default:
      dot.className = 'status-dot status-offline';
      text.textContent = 'Offline';
      callStatus.textContent = '';
  }
}

// Helper: Clear call info in dashboard
function clearCallInfo() {
  const callInfoArea = document.getElementById('callInfo');
  if (callInfoArea) {
    callInfoArea.innerHTML = '';
    callInfoArea.classList.add('hidden');
  }
}

// Fetch token and instantiate client on page load
async function createClientAndAttachListeners(host, token) {
  DashboardState.client = await SignalWire.SignalWire({ host, token, debug: { logWsTraffic: false } });
  if (!DashboardState.clientListenersAttached) {
    DashboardState.client.on('call.state', (params) => {
      if (params.call_state === 'created' && params.parent && params.parent.call_id) {
        fetch(`/api/call_info/${params.parent.call_id}`)
          .then(resp => resp.ok ? resp.json() : null)
          .then(data => {
            DashboardState.cachedCallInfo = data;
            applyCallInfoToUI(data);
          })
          .catch(() => {
            DashboardState.cachedCallInfo = null;
            applyCallInfoToUI(null);
          });
      }
      // Hide modal if call ended
      if (params.call_state === 'ended') {
        hideModal('incomingCallModal');
      }
    });
    DashboardState.clientListenersAttached = true;
  }
  DashboardState.subscriberInfo = await DashboardState.client.getSubscriberInfo();
  updateSubscriberUI(DashboardState.subscriberInfo);
}

// Helper: Reset UI after call ends
function resetAfterCallEnd() {
  if (hangupCallBtn) hangupCallBtn.classList.add('hidden');
  DashboardState.callAccepted = false;
  clearCallInfo();
  setDashboardStatus('online');
}

const goOnlineSpinner = document.createElement('span');
goOnlineSpinner.className = 'spinner-border text-info ms-2 hidden';
goOnlineSpinner.style.width = '1.5rem';
goOnlineSpinner.style.height = '1.5rem';
goOnlineSpinner.setAttribute('role', 'status');
if (goOnlineBtn && goOnlineBtn.parentNode) {
  goOnlineBtn.parentNode.insertBefore(goOnlineSpinner, goOnlineBtn.nextSibling);
}

if (goOnlineBtn) goOnlineBtn.onclick = async () => {
  setDashboardStatus('connecting');
  goOnlineBtn.disabled = true;
  showSpinner(goOnlineSpinner);
  goOnlineBtn.classList.add('hidden');
  let token = tokenInput ? tokenInput.value : '';
  const host = document.getElementById('host')?.value;
  let triedNewToken = false;
  let onlineSuccess = false;
  async function tryOnlineWithRetry(retries = 3, delay = 1500) {
    let attempt = 0;
    while (attempt < retries) {
      try {
        if (!DashboardState.client) {
          // If no client, fetch token and create
          const resp = await fetch('/api/create_sat', { method: 'POST' });
          const data = await resp.json();
          if (!data.token) throw new Error('Failed to get token');
          token = data.token;
          if (tokenInput) tokenInput.value = token;
          await createClientAndAttachListeners(host, token);
        }
        await DashboardState.client.online({ incomingCallHandlers: { all: handleIncomingCall } });
        return true;
      } catch (err) {
        if (!triedNewToken && (err.message?.includes('token') || err.message?.includes('401'))) {
          triedNewToken = true;
          const resp = await fetch('/api/create_sat', { method: 'POST' });
          const data = await resp.json();
          if (!data.token) throw new Error('Failed to get token');
          token = data.token;
          if (tokenInput) tokenInput.value = token;
          await createClientAndAttachListeners(host, token);
          continue;
        }
        await new Promise(res => setTimeout(res, delay));
        attempt++;
      }
    }
    return false;
  }
  onlineSuccess = await tryOnlineWithRetry();
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
};

function handleIncomingCall(notification) {
  DashboardState.invite = notification.invite;
  let callerIdName = DashboardState.invite.details.caller_id_name;
  let callerIdNumber = DashboardState.invite.details.caller_id_number;
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

async function handleRejectCall() {
  if (DashboardState.invite) {
    try { await DashboardState.invite.reject(); } catch (e) { console.error('Failed to reject call:', e); }
  }
  hideModal('incomingCallModal');
  DashboardState.callAccepted = false;
  clearCallInfo();
}
if (modalRejectCallBtn) modalRejectCallBtn.onclick = handleRejectCall;

setDashboardStatus('offline');
const showSubscriberInfoBtn = document.getElementById('showSubscriberInfo');
if (showSubscriberInfoBtn) {
  showSubscriberInfoBtn.onclick = function(e) {
    e.preventDefault();
    showModal('subscriberInfoModal');
  };
}

if (modalAcceptCallBtn) modalAcceptCallBtn.onclick = async () => {
  if (!DashboardState.invite) return;
  try {
    DashboardState.call = await DashboardState.invite.accept({ audio: true, video: false });
    setDashboardStatus('in-call');
    if (hangupCallBtn) {
      hangupCallBtn.classList.remove('hidden');
      hangupCallBtn.disabled = false;
    }
    DashboardState.callAccepted = true;
    applyCallInfoToUI(DashboardState.cachedCallInfo); // Now show call info in dashboard
    hideModal('incomingCallModal');
    DashboardState.call.on('destroy', resetAfterCallEnd);
  } catch (e) {
    alert('Failed to accept call: ' + e.message);
  }
};

// Wire up hangup button
if (hangupCallBtn) hangupCallBtn.onclick = async () => {
  if (DashboardState.call && typeof DashboardState.call.hangup === 'function') {
    try { await DashboardState.call.hangup(); } catch (err) {}
  }
  resetAfterCallEnd();
};

// Go Offline logic
if (goOfflineBtn) goOfflineBtn.onclick = async () => {
  if (DashboardState.client && typeof DashboardState.client.offline === 'function') {
    await DashboardState.client.offline();
  }
  setDashboardStatus('offline');
  goOfflineBtn.classList.add('hidden');
  goOnlineBtn.classList.remove('hidden');
  goOnlineBtn.disabled = false;
};

window.addEventListener('beforeunload', function () {
  if (DashboardState.call && typeof DashboardState.call.hangup === 'function') { try { DashboardState.call.hangup(); } catch (err) {} }
  if (DashboardState.client && typeof DashboardState.client.disconnect === 'function') { try { DashboardState.client.disconnect(); } catch (err) {} }
  // Notify backend that subscriber is going offline
  const email = DashboardState.subscriberInfo && DashboardState.subscriberInfo.email;
  const subscriberId = DashboardState.subscriberInfo && DashboardState.subscriberInfo.id;
  if (subscriberId) {
    navigator.sendBeacon(`/api/subscriber_offline/${subscriberId}`);
  }
}); 