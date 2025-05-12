/**
 * call/api.js
 * 
 * API-related functions for the call widget page.
 * Handles token fetching and API interactions.
 */

import { fetchAPI } from '../../utils.js';

// Constants
const MAX_FETCH_ATTEMPTS = 3;
const RETRY_DELAY_MS = 1000;

// Track token fetching attempts
let fetchTokenAttempts = 0;

// Fetch widget configuration from the server
export async function getWidgetConfig() {
    try {
        console.log('Requesting token for widget');
        fetchTokenAttempts++;
        
        // Use fetchAPI helper
        const data = await fetchAPI('/api/widget_config', {
            method: 'POST',
            body: JSON.stringify({})
        });
        
        // Reset attempt counter on success
        fetchTokenAttempts = 0;
        console.log('Successfully obtained token');
        return data;
    } catch (error) {
        console.error('Widget config error:', error);
        
        // Retry logic for token fetch failures
        if (fetchTokenAttempts < MAX_FETCH_ATTEMPTS) {
            console.log(`Retrying token fetch (attempt ${fetchTokenAttempts}/${MAX_FETCH_ATTEMPTS})...`);
            await new Promise(resolve => setTimeout(resolve, RETRY_DELAY_MS)); // Wait 1 second
            return getWidgetConfig(); // Recursively retry
        }
        
        throw error;
    }
}

// Submit member creation form
export async function createMember(formData, endpoint = '/api/create_member') {
    console.log(`Creating member with data:`, formData);
    
    try {
        // Direct fetch approach with detailed logging
        console.log(`Posting to ${endpoint} with JSON data`);
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        console.log(`Received response with status: ${response.status}`);
        const responseData = await response.json();
        console.log(`Response data:`, responseData);
        
        if (!response.ok || (responseData && responseData.error)) {
            throw new Error(responseData.message || `API error (${response.status})`);
        }
        
        // Return the data portion
        return responseData.data || responseData;
    } catch (error) {
        console.error('Create member error:', error);
        throw error;
    }
} 