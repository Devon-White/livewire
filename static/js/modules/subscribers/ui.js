/**
 * subscribers/ui.js
 * 
 * UI-related functions for the agent dashboard (subscriber.html).
 * Handles all DOM manipulations, status updates, and modal interactions.
 */


// Helper: Update subscriber info in UI
export function updateSubscriberUI(info) {
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
export function showModal(id) {
  var modal = bootstrap.Modal.getOrCreateInstance(document.getElementById(id));
  modal.show();
}

export function hideModal(id) {
  var modal = bootstrap.Modal.getOrCreateInstance(document.getElementById(id));
  modal.hide();
}

// Helper: Format caller info for modal/dashboard
export function formatCallerInfo(data, labelName = 'Name', labelSummary = 'Summary') {
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
export function applyCallInfoToUI(data, callAccepted) {
  const incomingSummary = document.getElementById('incomingCallerSummary');
  if (incomingSummary) incomingSummary.innerHTML = formatCallerInfo(data, 'Name', 'Summary');
  const callInfoArea = document.getElementById('callInfo');
  if (callInfoArea) {
    callInfoArea.innerHTML = formatCallerInfo(data, 'Caller', 'Summary');
    if (callAccepted) {
      callInfoArea.classList.remove('hidden');
    } else {
      callInfoArea.classList.add('hidden');
    }
  }
}

// Helper: Set dashboard status dot, text, and call status text
export function setDashboardStatus(state) {
  const dot = document.getElementById('statusDot');
  const text = document.getElementById('statusText');
  const callStatus = document.getElementById('callStatus');
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
export function clearCallInfo() {
  const callInfoArea = document.getElementById('callInfo');
  if (callInfoArea) {
    callInfoArea.innerHTML = '';
    callInfoArea.classList.add('hidden');
  }
}

// Creates and returns a spinner element for the go online button
export function createGoOnlineSpinner() {
  const spinner = document.createElement('span');
  spinner.className = 'spinner-border text-info ms-2 hidden';
  spinner.style.width = '1.5rem';
  spinner.style.height = '1.5rem';
  spinner.setAttribute('role', 'status');
  return spinner;
}

// Reset UI after call ends
export function resetAfterCallEnd(hangupCallBtn) {
  if (hangupCallBtn) hangupCallBtn.classList.add('hidden');
  clearCallInfo();
  setDashboardStatus('online');
} 