/**
 * forms/validation.js
 * 
 * Shared form validation functions used across multiple forms in the application.
 * Provides consistent validation for email, passwords, names, and other form fields.
 */

// Constants
export const DEFAULT_PASSWORD_MIN_LENGTH = 8;
export const PHONE_REGEX = /^[+]?[(]?[0-9]{3}[)]?[-\s.]?[0-9]{3}[-\s.]?[0-9]{4,6}$/;

// Validates an email address
export function validateEmail(email) {
  if (!email || email.trim() === '') {
    return { valid: false, message: 'Email is required' };
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return { valid: false, message: 'Please enter a valid email address' };
  }
  
  return { valid: true };
}

// Validates a password
export function validatePassword(password, minLength = DEFAULT_PASSWORD_MIN_LENGTH) {
  if (!password || password.trim() === '') {
    return { valid: false, message: 'Password is required' };
  }
  
  if (password.length < minLength) {
    return { valid: false, message: `Password must be at least ${minLength} characters` };
  }
  
  return { valid: true };
}

// Validates text input (names, etc.) for required fields
export function validateRequiredField(value, fieldName) {
  if (!value || value.trim() === '') {
    return { valid: false, message: `${fieldName} is required` };
  }
  
  return { valid: true };
}

// Validates phone number format
export function validatePhone(phone) {
  if (!phone || phone.trim() === '') {
    return { valid: true }; // Phone might be optional
  }
  
  // Basic phone validation (accepts country codes, spaces, dashes)
  const phoneRegex = PHONE_REGEX;
  if (!phoneRegex.test(phone)) {
    return { valid: false, message: 'Please enter a valid phone number' };
  }
  
  return { valid: true };
}

// Validates form data with multiple fields
export function validateForm(formData, rules) {
  const errors = {};
  let isValid = true;
  
  // Process each field according to its rules
  for (const field in rules) {
    const value = formData[field];
    const fieldRules = rules[field];
    
    let fieldResult = { valid: true };
    
    // Apply each rule to the field
    for (const rule of fieldRules) {
      switch (rule.type) {
        case 'required':
          fieldResult = validateRequiredField(value, rule.name || field);
          break;
        case 'email':
          fieldResult = validateEmail(value);
          break;
        case 'password':
          fieldResult = validatePassword(value, rule.minLength);
          break;
        case 'phone':
          fieldResult = validatePhone(value);
          break;
        case 'match':
          const matchValue = formData[rule.field];
          if (value !== matchValue) {
            fieldResult = { 
              valid: false, 
              message: rule.message || `${field} must match ${rule.field}` 
            };
          }
          break;
      }
      
      // Break on first invalid rule for this field
      if (!fieldResult.valid) {
        errors[field] = fieldResult.message;
        isValid = false;
        break;
      }
    }
  }
  
  return { isValid, errors };
}

// Shows validation errors on a form
export function showValidationErrors(errors, formElement) {
  // Clear previous error messages
  const previousErrors = formElement.querySelectorAll('.invalid-feedback');
  previousErrors.forEach(el => el.remove());
  
  // Remove invalid classes
  formElement.querySelectorAll('.is-invalid').forEach(el => {
    el.classList.remove('is-invalid');
  });
  
  // Show new error messages
  for (const field in errors) {
    const inputElement = formElement.querySelector(`[name="${field}"]`);
    if (!inputElement) continue;
    
    // Add invalid class
    inputElement.classList.add('is-invalid');
    
    // Create and show error message
    const errorElement = document.createElement('div');
    errorElement.className = 'invalid-feedback';
    errorElement.textContent = errors[field];
    
    // Insert after the input
    inputElement.parentNode.insertBefore(errorElement, inputElement.nextSibling);
  }
}

// Extracts form data as an object
export function getFormData(formElement) {
  const formData = {};
  const formElements = formElement.elements;
  
  for (let i = 0; i < formElements.length; i++) {
    const element = formElements[i];
    if (element.name) {
      // Handle different input types
      if (element.type === 'checkbox') {
        formData[element.name] = element.checked;
      } else if (element.type !== 'submit' && element.type !== 'button') {
        formData[element.name] = element.value;
      }
    }
  }
  
  return formData;
} 