/**
 * call/api.js
 * 
 * API-related functions for the call widget page.
 * Handles token fetching and API interactions.
 */

import { fetchAPI } from '../../utils.js';

// Track token fetching attempts
let fetchTokenAttempts = 0;
const MAX_FETCH_ATTEMPTS = 3;

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
            await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
            return getWidgetConfig(); // Recursively retry
        }
        
        throw error;
    }
}

// Submit member creation form
export async function createMember(formData) {
    try {
        // Use fetchAPI helper
        const data = await fetchAPI('/api/create_member', {
            method: 'POST',
            body: JSON.stringify(formData)
        });
        
        return data;
    } catch (error) {
        console.error('Create member error:', error);
        throw error;
    }
} 