/**
 * forms/index.js
 * 
 * Entry point for forms module.
 * Exports all functionality from the forms sub-modules.
 * This pattern provides a clean public API for the module.
 */

// Re-export everything from the validation module
export * from './validation.js';

// Export the specific form implementations
export * from './signup.js';
export * from './create-member.js'; 