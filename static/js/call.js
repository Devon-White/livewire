/*
 * call.js
 * Handles SignalWire call widget setup and event handling for the call page (call.html).
 */

let client = null;
let call = null;
let currentCallId = null;

async function getWidgetConfig() {
    const resp = await fetch('/api/widget_config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    });
    if (!resp.ok) throw new Error('Failed to fetch widget config');
    return await resp.json();
}

// --- Create Member Modal Logic ---
function showCreateMemberModal() {
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
                <label class="form-label">Email <span class="text-danger">*</span></label>
                <input type="email" name="email" class="form-control" required>
                <div class="invalid-feedback">Email is required.</div>
              </div>
              <div class="mb-3">
                <label class="form-label">Password <span class="text-danger">*</span></label>
                <input type="password" name="password" id="createMemberPassword" class="form-control" required minlength="8" autocomplete="new-password">
                <div class="invalid-feedback" id="createMemberPasswordLengthError">Password must be at least 8 characters.</div>
                <div class="invalid-feedback">Password is required.</div>
              </div>
              <div class="mb-3">
                <label class="form-label">Confirm Password <span class="text-danger">*</span></label>
                <input type="password" name="confirm_password" id="createMemberConfirmPassword" class="form-control" required autocomplete="new-password">
                <div class="invalid-feedback" id="createMemberPasswordMatchError">Passwords do not match.</div>
                <div class="invalid-feedback">Confirm password is required.</div>
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
                <label class="form-label">Timezone</label>
                <input type="text" name="timezone" class="form-control">
              </div>
              <div class="mb-3">
                <label class="form-label">Country</label>
                <input type="text" name="country" class="form-control">
              </div>
              <div class="mb-3">
                <label class="form-label">Region</label>
                <input type="text" name="region" class="form-control">
              </div>
              <div class="mb-3">
                <label class="form-label">Company Name</label>
                <input type="text" name="company_name" class="form-control">
              </div>
              <button id="createMemberBtn" type="button" class="demo-button w-100 mt-3">Create Member</button>
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

    // Validation and submit logic (duplicated from signup.js for now)
    document.getElementById('createMemberBtn').onclick = function(e) {
      e.preventDefault();
      let valid = true;
      ['first_name', 'last_name', 'email', 'password', 'confirm_password'].forEach(id => {
        const input = document.querySelector(`#createMemberForm [name="${id}"]`);
        if (input && !input.value.trim()) {
          input.classList.add('is-invalid');
          valid = false;
        } else if (input) {
          input.classList.remove('is-invalid');
        }
      });
      const password = document.getElementById('createMemberPassword').value;
      if (password.length < 8) {
        document.getElementById('createMemberPassword').classList.add('is-invalid');
        document.getElementById('createMemberPasswordLengthError').style.display = 'block';
        valid = false;
      } else {
        document.getElementById('createMemberPassword').classList.remove('is-invalid');
        document.getElementById('createMemberPasswordLengthError').style.display = 'none';
      }
      const confirmPassword = document.getElementById('createMemberConfirmPassword').value;
      if (password !== confirmPassword) {
        document.getElementById('createMemberConfirmPassword').classList.add('is-invalid');
        document.getElementById('createMemberPasswordMatchError').style.display = 'block';
        valid = false;
      } else {
        document.getElementById('createMemberConfirmPassword').classList.remove('is-invalid');
        document.getElementById('createMemberPasswordMatchError').style.display = 'none';
      }
      if (valid) {
        // Ensure call_id is included in the form data
        if (callIdInput && currentCallId) {
            callIdInput.value = currentCallId;
        }
        const form = document.getElementById('createMemberForm');
        const formData = new FormData(form);
        fetch('/api/create_member', {
          method: 'POST',
          body: formData
        }).then(async resp => {
          if (resp.ok) {
            const data = await resp.json();
            bootstrap.Modal.getOrCreateInstance(document.getElementById('createMemberModal')).hide();
            if (data.member_id) {
              showMemberIdModal(data.member_id);
            } else {
              alert('Member created!');
            }
          } else {
            alert('Failed to create member.');
          }
        }).catch(() => {
          alert('Network error.');
        });
      }
    };

    // Show modal
    var modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('createMemberModal'));
    modal.show();
}

// --- Hook into user_event ---
function handleUserEvent(params) {
    console.log("handleUserEvent", params);
    if (params.type === "create_member") {
        showCreateMemberModal();
    }
}

function setupCallWidget() {
    const callButton = document.getElementById('callButton');
    if (!callButton) {
        console.error('callButton element not found in the DOM');
        return;
    }

    getWidgetConfig().then(config => {
        // Create the widget element
        const widgetHtml = /*html*/`
            <c2c-widget
                buttonId="${callButton.id}"
                collectUserDetails="false"
                userVariables="{}"
                callDetails='${JSON.stringify({
                    destination: config.destination,
                    supportsVideo: false,
                    supportsAudio: true
                })}'
                token="${config.guest_token}">
            </c2c-widget>
        `;
        
        // Insert the widget HTML after the call button
        callButton.insertAdjacentHTML('afterend', widgetHtml);

        const widget = document.querySelector('c2c-widget');

        // Attach other event listeners as before
        widget.addEventListener("beforecall", () => {
            console.log("beforecall");
            ['ci-SAT', 'pt-SAT', 'as-SAT'].forEach(key => sessionStorage.removeItem(key));
        });
        widget.addEventListener("call.joined", ({ detail }) => {
            client = detail.client;
            call = detail.call;
            // Set the call_id from activeRTCPeerId
            if (call && call.activeRTCPeerId) {
                currentCallId = call.activeRTCPeerId;
            }
            client.on("user_event", (event) => {
                console.log("user_event", event);
                handleUserEvent(event);
            });
            console.log("call.joined", detail);
        });
        widget.addEventListener("call.left", ({ detail }) => {
            console.log("call.left", detail);
            client = null;
            call = null;
            currentCallId = null;
        });
    }).catch(err => {
        alert('Failed to get guest token: ' + err.message);
    });
}

document.addEventListener('DOMContentLoaded', setupCallWidget);

// Utility to show a styled modal alert for the member ID
function showMemberIdModal(memberId) {
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
            <div class="fw-bold fs-3 mb-3" style="color:var(--sw-pink);">${memberId}</div>
            <div class="mb-2">Please <b>save this ID</b> for future verification.</div>
          </div>
          <div class="modal-footer border-0 d-flex justify-content-center" style="background:rgba(12,19,57,0.95);">
            <button type="button" class="btn btn-primary" style="background:var(--sw-gradient); border:none;" data-bs-dismiss="modal">OK</button>
          </div>
        </div>
      </div>
    </div>`;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    var modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('memberIdModal'));
    modal.show();
}