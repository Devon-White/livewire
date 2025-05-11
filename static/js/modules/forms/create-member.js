/**
 * forms/create-member.js
 * 
 * Handles validation and submission of the create member form in the call widget modal.
 * Uses the shared form validation module for consistent validation.
 */

import { validateForm, showValidationErrors, getFormData } from './validation.js';
import { showMemberIdModal } from '../call/ui.js'; // Import the showMemberIdModal function
import { createMember } from '../call/api.js';

export function initCreateMemberForm() {
  const memberForm = document.getElementById('createMemberForm');
  if (!memberForm) return;
  
  // Define validation rules for the create member form
  const validationRules = {
    first_name: [{ type: 'required', name: 'First Name' }],
    last_name: [{ type: 'required', name: 'Last Name' }],
    summary: [{ type: 'required', name: 'Summary' }],
    email: [
      { type: 'required', name: 'Email' },
      { type: 'email' }
    ],
    phone: [{ type: 'phone' }]
  };
  
  // Handle form submission
  memberForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = getFormData(memberForm);
    const validation = validateForm(formData, validationRules);
    
    if (!validation.isValid) {
      showValidationErrors(validation.errors, memberForm);
      return;
    }
    
    // Show loading state
    const submitBtn = memberForm.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Submitting...';
    
    try {
      // Use createMember helper
      const response = await createMember(formData);
      
      // Hide the create member modal
      try {
        bootstrap.Modal.getInstance(document.getElementById('createMemberModal')).hide();
      } catch (modalError) {
        console.error('Error hiding modal:', modalError);
      }
      
      // Reset the form
      memberForm.reset();
      
      // Show the member ID modal with the new member ID
      if (response && response.member_id) {
        showMemberIdModal(response.member_id);
      }
      
    } catch (error) {
      console.error('Error submitting form:', error);
      
      // Show error message
      const errorElement = document.createElement('div');
      errorElement.className = 'alert alert-danger mt-3';
      errorElement.textContent = error.message || 'Error creating member. Please try again.';
      memberForm.prepend(errorElement);
      
      // Remove error message after 5 seconds
      setTimeout(() => {
        if (errorElement.parentNode) {
          errorElement.parentNode.removeChild(errorElement);
        }
      }, 5000);
    } finally {
      // Restore button state
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
    }
  });
} 