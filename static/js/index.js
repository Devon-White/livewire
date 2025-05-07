import { showSpinner, hideSpinner } from './utils.js';
document.getElementById('stage1').addEventListener('submit', async function(e) {
  e.preventDefault();
  const form = e.target;
  const submitBtn = document.getElementById('indexSubmitBtn');
  const loading = document.getElementById('indexLoading');
  submitBtn.disabled = true;
  showSpinner(loading);
  const data = new FormData(form);
  try {
    const resp = await fetch('/', {
      method: 'POST',
      body: data
    });
    if (resp.redirected) {
      // Now create/update the SWML handler
      const handlerResp = await fetch('/api/swml_handler', { method: 'POST' });
      if (handlerResp.ok) {
        // Now get widget config (guest token + destination)
        const configResp = await fetch('/api/widget_config', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({})
        });
        if (configResp.ok) {
          const config = await configResp.json();
          sessionStorage.setItem('widgetConfig', JSON.stringify(config));
          window.location.href = '/call';
        } else {
          const err = await configResp.json();
          alert('Failed to get widget config: ' + (err.error || configResp.status));
        }
      } else {
        const err = await handlerResp.json();
        alert('Failed to create SWML handler: ' + (err.error || handlerResp.status));
      }
    } else {
      alert('Failed to store credentials.');
    }
  } catch (err) {
    alert('Network error. Please try again.');
  }
  submitBtn.disabled = false;
  hideSpinner(loading);
}); 