/**
 * forms/create-member.js
 * 
 * Handles the create member form submission in the modal.
 */

import { showMemberIdModal } from '../call/ui.js';

export function initCreateMemberForm() {
  console.log('Initializing create member form');
  
  // Scope to the modal to avoid duplicate IDs
  const modal = document.getElementById('createMemberModal');
  if (!modal) {
    console.error('Create member modal not found');
    return;
  }
  const form = modal.querySelector('form');
  const submitBtn = modal.querySelector('.member-submit-btn');
  
  if (!form) {
    console.error('Create member form not found');
    return;
  }
  
  if (!submitBtn) {
    console.error('Submit button not found');
    return;
  }
  
  console.log('Found form and submit button, attaching click handler');
  
  // Remove any previous click handlers to avoid duplicates
  submitBtn.replaceWith(submitBtn.cloneNode(true));
  const newSubmitBtn = modal.querySelector('.member-submit-btn');

  newSubmitBtn.addEventListener('click', async function(event) {
    console.log('Submit button clicked');
    
    // Collect form data
    const formData = {};
    const formElements = form.elements;
    
    // Basic form validation
    let isValid = true;
    let errorMessage = '';
    
    // Loop through form fields and validate
    for (let i = 0; i < formElements.length; i++) {
      const element = formElements[i];
      
      // Skip buttons and non-input elements
      if (element.tagName !== 'INPUT' && element.tagName !== 'SELECT' && element.tagName !== 'TEXTAREA') {
        continue;
      }
      
      // Skip elements without a name
      if (!element.name) {
        continue;
      }
      
      // Get the value, trimming whitespace for text inputs
      const value = element.type === 'text' || element.type === 'email' ? 
                    element.value.trim() : element.value;
      
      // Add to form data
      formData[element.name] = value;
      
      // Check required fields
      if (element.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = `${element.name.replace('_', ' ')} is required`;
        element.classList.add('is-invalid');
      } else {
        element.classList.remove('is-invalid');
      }
    }
    
    // Password match validation
    if (formData.password !== formData.confirm_password) {
      isValid = false;
      errorMessage = 'Passwords do not match';
      form.querySelector('[name="confirm_password"]').classList.add('is-invalid');
    }
    
    // If validation fails, show error and stop
    if (!isValid) {
      console.error('Validation failed:', errorMessage);
      showError(form, errorMessage);
      return;
    }
    
    // Show loading state
    console.log('Form validated, submitting data', formData);
    const originalText = newSubmitBtn.textContent;
    newSubmitBtn.disabled = true;
    newSubmitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Creating...';
    
    try {
      // Add call_id if available
      if (modal && modal.dataset.callId) {
        formData.call_id = modal.dataset.callId;
      }
      
      // Submit the form data to the API
      const response = await fetch('/api/create_member', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      
      // Parse the response
      const data = await response.json();
      console.log('API response:', data);
      
      if (!response.ok) {
        throw new Error(data.message || 'Failed to create member');
      }
      
      // Hide the modal
      if (modal && window.bootstrap) {
        const modalInstance = bootstrap.Modal.getInstance(modal);
        if (modalInstance) {
          modalInstance.hide();
        }
      }
      
      // Reset the form
      form.reset();
      
      // Show success with member ID
      if (data.data && data.data.member_id) {
        showMemberIdModal(data.data.member_id);
      }
    } catch (error) {
      console.error('Submission error:', error);
      showError(form, error.message || 'Failed to create member');
    } finally {
      // Restore button state
      newSubmitBtn.disabled = false;
      newSubmitBtn.innerHTML = originalText;
    }
  });
  
  // Helper function to show error message
  function showError(form, message) {
    // Remove any existing error messages
    const existingError = form.querySelector('.alert-danger');
    if (existingError) {
      existingError.remove();
    }
    
    // Create and insert error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger mt-3';
    errorDiv.textContent = message;
    form.insertBefore(errorDiv, form.firstChild);
    
    // Remove error after 5 seconds
    setTimeout(() => {
      if (errorDiv.parentNode) {
        errorDiv.remove();
      }
    }, 5000);
  }
} 