/**
 * subscribers/index.js
 * 
 * Entry point for the subscribers module.
 * Exports all functionality from the subscribers sub-modules.
 * This pattern provides a clean public API for the module.
 */

// Re-export everything from the individual modules
export * from './state.js';
export * from './ui.js';
export * from './client.js';

// Export the main functionality from the implementation file
export * from './main.js'; 