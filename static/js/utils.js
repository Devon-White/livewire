// Spinner utility functions for global use
export function showSpinner(spinner) {
  if (spinner) spinner.classList.remove('hidden');
}
export function hideSpinner(spinner) {
  if (spinner) spinner.classList.add('hidden');
} 