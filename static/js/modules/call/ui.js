/**
 * call/ui.js
 * 
 * UI-related functions for the call widget page.
 * Handles modals and other UI elements.
 */

// Create and show the member creation modal
export function showCreateMemberModal(currentCallId) {
    // Remove existing modal if present
    const existing = document.getElementById('createMemberModal');
    if (existing) existing.remove();

    // Modal HTML (adapted from signup.html)
    const modalHtml = /*html*/`
    <div class="modal fade" id="createMemberModal" tabindex="-1" aria-labelledby="createMemberModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content bg-dark text-white border-0">
          <div class="modal-header border-0" style="background:rgba(12,19,57,0.95);">
            <h5 class="modal-title" id="createMemberModalLabel">Create Member</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body" style="background:rgba(12,19,57,0.85);">
            <form id="createMemberForm" autocomplete="off">
              <input type="hidden" name="call_id" id="createMemberCallId" value="">
              <div class="mb-2 text small">Fields marked with <span class="text-danger">*</span> are required.</div>
              <div class="mb-3">
                <label class="form-label">First Name <span class="text-danger">*</span></label>
                <input type="text" name="first_name" class="form-control" required>
                <div class="invalid-feedback">First name is required.</div>
              </div>
              <div class="mb-3">
                <label class="form-label">Last Name <span class="text-danger">*</span></label>
                <input type="text" name="last_name" class="form-control" required>
                <div class="invalid-feedback">Last name is required.</div>
              </div>
              <div class="mb-3">
                <label class="form-label">Summary <span class="text-danger">*</span></label>
                <textarea name="summary" class="form-control" required 
                          placeholder="Brief description of why you're calling"></textarea>
                <div class="invalid-feedback">Summary is required.</div>
              </div>
              <div class="mb-3">
                <label class="form-label">Email <span class="text-danger">*</span></label>
                <input type="email" name="email" class="form-control" required>
                <div class="invalid-feedback">Email is required.</div>
              </div>
              <div class="mb-3">
                <label class="form-label">Phone</label>
                <input type="tel" name="phone" class="form-control">
                <div class="invalid-feedback">Please enter a valid phone number.</div>
              </div>
              <div class="mb-3">
                <label class="form-label">Display Name</label>
                <input type="text" name="display_name" class="form-control">
              </div>
              <div class="mb-3">
                <label class="form-label">Job Title</label>
                <input type="text" name="job_title" class="form-control">
              </div>
              <div class="mb-3">
                <label class="form-label">Company Name</label>
                <input type="text" name="company_name" class="form-control">
              </div>
              <button type="submit" class="demo-button w-100 mt-3">Create Member</button>
            </form>
          </div>
        </div>
      </div>
    </div>`;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // Set the call_id hidden input value
    const callIdInput = document.getElementById('createMemberCallId');
    if (callIdInput && currentCallId) {
        callIdInput.value = currentCallId;
    }

    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('createMemberModal'));
    modal.show();
    
    return modal;
}

// Show a styled modal alert for the member ID
export function showMemberIdModal(memberId) {
    // Remove existing modal if present
    const existing = document.getElementById('memberIdModal');
    if (existing) existing.remove();
    
    const modalHtml = /*html*/`
    <div class="modal fade" id="memberIdModal" tabindex="-1" aria-labelledby="memberIdModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content bg-dark text-white border-0">
          <div class="modal-header border-0" style="background:rgba(12,19,57,0.95);">
            <h5 class="modal-title" id="memberIdModalLabel">Member Created</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body text-center" style="background:rgba(12,19,57,0.85);">
            <div class="fs-5 mb-3">Your Member ID is:</div>
            <div class="d-flex align-items-center justify-content-center mb-3">
              <div id="memberId" class="fw-bold fs-3 me-2" style="color:var(--sw-pink);">${memberId}</div>
              <button id="copyMemberIdBtn" class="btn btn-sm" style="background:rgba(255,255,255,0.1); color:white;">
                <i class="bi bi-clipboard"></i> Copy
              </button>
            </div>
            <div class="mb-2">Please <b>save this ID</b> for future verification.</div>
          </div>
          <div class="modal-footer border-0 d-flex justify-content-center" style="background:rgba(12,19,57,0.95);">
            <button type="button" class="btn btn-primary" style="background:var(--sw-gradient); border:none;" data-bs-dismiss="modal">OK</button>
          </div>
        </div>
      </div>
    </div>`;
    
    // Insert the modal into the DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Get DOM references
    const modalElement = document.getElementById('memberIdModal');
    const copyButton = document.getElementById('copyMemberIdBtn');
    
    // Setup event handlers only if elements exist
    if (modalElement && copyButton) {
        // Create Bootstrap modal instance
        const modalInstance = new bootstrap.Modal(modalElement);
        
        // Copy functionality
        const handleCopy = () => {
            navigator.clipboard.writeText(memberId)
                .then(() => {
                    copyButton.innerHTML = '<i class="bi bi-check"></i> Copied';
                    setTimeout(() => {
                        // Only update if button still exists in DOM
                        if (document.body.contains(copyButton)) {
                            copyButton.innerHTML = '<i class="bi bi-clipboard"></i> Copy';
                        }
                    }, 2000);
                })
                .catch(err => console.error('Failed to copy member ID:', err));
        };
        
        // One-time cleanup when modal hides
        const handleHidden = () => {
            // Remove all event listeners
            copyButton.removeEventListener('click', handleCopy);
            modalElement.removeEventListener('hidden.bs.modal', handleHidden);
            
            // Remove from DOM
            if (document.body.contains(modalElement)) {
                document.body.removeChild(modalElement);
            }
        };
        
        // Add event listeners
        copyButton.addEventListener('click', handleCopy);
        modalElement.addEventListener('hidden.bs.modal', handleHidden);
        
        // Show the modal
        modalInstance.show();
        
        return modalInstance;
    }
    
    return null;
}

// Create the widget HTML
export function createWidgetHtml(callButtonId, config) {
    // The SignalWire Call Widget expects a buttonId attribute that references 
    // the ID of the button that will trigger the call
    return /*html*/`
        <c2c-widget
            buttonId="${callButtonId}"
            collectUserDetails="false"
            callDetails='${JSON.stringify({
                destination: config.destination,
                supportsVideo: false,
                supportsAudio: true
            })}'
            token="${config.guest_token}">
        </c2c-widget>
    `;
} 