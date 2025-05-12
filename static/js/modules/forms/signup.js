/**
 * forms/signup.js
 * 
 * Handles client-side validation and modal confirmation for the signup page (signup.html).
 * Uses the shared form validation module for consistent validation.
 */

import { validateForm, showValidationErrors, getFormData, DEFAULT_PASSWORD_MIN_LENGTH } from './validation.js';

document.addEventListener('DOMContentLoaded', () => {
  const signupForm = document.getElementById('signupForm');
  const confirmSignupBtn = document.getElementById('confirmSignupBtn');
  
  if (!signupForm || !confirmSignupBtn) return;
  
  // Define validation rules for the signup form
  const validationRules = {
    first_name: [{ type: 'required', name: 'First Name' }],
    last_name: [{ type: 'required', name: 'Last Name' }],
    email: [
      { type: 'required', name: 'Email' },
      { type: 'email' }
    ],
    password: [
      { type: 'required', name: 'Password' },
      { type: 'password', minLength: DEFAULT_PASSWORD_MIN_LENGTH }
    ],
    confirm_password: [
      { type: 'required', name: 'Confirm Password' },
      { type: 'match', field: 'password', message: 'Passwords do not match' }
    ]
  };
  
  // Handle form submission via button click
  const submitBtn = signupForm.querySelector('button[type="submit"]');
  if (submitBtn) {
    submitBtn.addEventListener('click', function(e) {
      e.preventDefault();
      validateAndShowModal();
    });
  }
  
  // Validation function
  function validateAndShowModal() {
    const formData = getFormData(signupForm);
    const validation = validateForm(formData, validationRules);
    
    if (validation.isValid) {
      // Show confirmation modal
      new bootstrap.Modal(document.getElementById('confirmModal')).show();
    } else {
      // Show validation errors
      showValidationErrors(validation.errors, signupForm);
    }
  }
  
  // Handle confirm signup button click - submit the regular form
  confirmSignupBtn.onclick = function() {
    // Submit form normally - it will use the standard HTML form submission
    signupForm.submit();
  };
}); 