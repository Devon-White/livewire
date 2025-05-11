/**
 * call/index.js
 * 
 * Entry point for call module.
 * Exports all functionality from the call sub-modules.
 * This pattern provides a clean public API for the module.
 */

// Re-export everything from the individual modules
export * from './api.js';
export * from './ui.js';

// Export the main functionality from the implementation file
export * from './main.js';