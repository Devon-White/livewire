/**
 * Shared utility functions for the LiveWire demo frontend.
 * These functions can be imported by any module.
 */

// UI Helpers
/**
 * Shows a spinner element by removing the 'hidden' class
 * @param {HTMLElement} spinner - The spinner element to show
 */
export function showSpinner(spinner) {
  if (spinner) spinner.classList.remove('hidden');
}

/**
 * Hides a spinner element by adding the 'hidden' class
 * @param {HTMLElement} spinner - The spinner element to hide
 */
export function hideSpinner(spinner) {
  if (spinner) spinner.classList.add('hidden');
}

// API Helpers
/**
 * Makes a fetch API call with standardized error handling
 * @param {string} url - The URL to fetch
 * @param {Object} options - Fetch options
 * @returns {Promise<Object>} - The JSON response data
 * @throws {Error} - If the request fails
 */
export async function fetchAPI(url, options = {}) {
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });
    
    const data = await response.json();
    
    if (!response.ok || (data && data.error)) {
      throw new Error(data.message || `API error (${response.status})`);
    }
    
    // Verify standard format
    if (!data.success || !data.data) {
      throw new Error('Invalid API response format');
    }
    
    // Return the data portion directly
    return data.data;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}