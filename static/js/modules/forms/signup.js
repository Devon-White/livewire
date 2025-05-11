/**
 * forms/signup.js
 * 
 * Handles client-side validation and modal confirmation for the signup page (signup.html).
 * Uses the shared form validation module for consistent validation.
 */

import { validateForm, showValidationErrors, getFormData } from './validation.js';

document.addEventListener('DOMContentLoaded', () => {
  const signupForm = document.getElementById('signupForm');
  const signupBtn = document.getElementById('signupBtn');
  const confirmSignupBtn = document.getElementById('confirmSignupBtn');
  
  if (!signupForm || !signupBtn || !confirmSignupBtn) return;
  
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
      { type: 'password', minLength: 8 }
    ],
    confirm_password: [
      { type: 'required', name: 'Confirm Password' },
      { type: 'match', field: 'password', message: 'Passwords do not match' }
    ]
  };
  
  // Handle signup button click
  signupBtn.onclick = function(e) {
    e.preventDefault();
    
    const formData = getFormData(signupForm);
    const validation = validateForm(formData, validationRules);
    
    if (validation.isValid) {
      // Show confirmation modal
      new bootstrap.Modal(document.getElementById('confirmModal')).show();
    } else {
      // Show validation errors
      showValidationErrors(validation.errors, signupForm);
    }
  };
  
  // Handle confirm signup button click
  confirmSignupBtn.onclick = function() {
    signupForm.submit();
  };
}); 