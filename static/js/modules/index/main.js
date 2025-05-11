/**
 * index/main.js
 * 
 * Main implementation for the index page.
 * Handles submitting credentials and setting up the SWML handler.
 */

import { showSpinner, hideSpinner, fetchAPI } from '../../utils.js';

// Handle form submission
export async function handleFormSubmission(e) {
  e.preventDefault();
  const form = e.target;
  const submitBtn = document.getElementById('indexSubmitBtn');
  const loading = document.getElementById('indexLoading');
  
  submitBtn.disabled = true;
  showSpinner(loading);
  
  const data = new FormData(form);
  
  try {
    console.log('Submitting credentials...');
    const resp = await fetch('/', {
      method: 'POST',
      body: data
    });
    
    if (resp.redirected) {
      // Now create/update the SWML handler
      console.log('Creating SWML handler...');
      try {
        await fetchAPI('/api/swml_handler', { 
          method: 'POST',
          body: JSON.stringify({})
        });
        
        // Redirect to the call page
        console.log('SWML handler created successfully, redirecting to call page');
        window.location.href = '/call';
      } catch (error) {
        throw new Error(error.message || 'Failed to create SWML handler');
      }
    } else {
      throw new Error('Failed to store credentials');
    }
  } catch (err) {
    console.error('Error in form submission:', err);
    alert(err.message || 'Network error. Please try again.');
  }
  
  submitBtn.disabled = false;
  hideSpinner(loading);
}

// Set up event listeners
export function initIndexPage() {
  const form = document.getElementById('stage1');
  if (form) {
    form.addEventListener('submit', handleFormSubmission);
  }
}

// Initialize when the DOM is ready
document.addEventListener('DOMContentLoaded', initIndexPage); 