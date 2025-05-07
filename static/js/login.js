import { showSpinner, hideSpinner } from './utils.js';

document.getElementById('loginForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  const form = e.target;
  const loginBtn = document.getElementById('loginBtn');
  const loading = document.getElementById('loginLoading');
  loginBtn.disabled = true;
  showSpinner(loading);
  const data = new FormData(form);
  let errorMsg = null;
  try {
    const resp = await fetch('/login', {
      method: 'POST',
      body: data
    });
    if (resp.redirected) {
      window.location.href = resp.url;
      return;
    } else if (resp.ok) {
      // If not redirected, check for error in HTML
      const html = await resp.text();
      if (html.includes('alert-danger')) {
        // Extract error message from HTML
        const temp = document.createElement('div');
        temp.innerHTML = html;
        const alert = temp.querySelector('.alert-danger');
        errorMsg = alert ? alert.textContent : 'Login failed.';
      }
    } else {
      errorMsg = 'Login failed. Please try again.';
    }
  } catch (err) {
    errorMsg = 'Network error. Please try again.';
  }
  loginBtn.disabled = false;
  hideSpinner(loading);
  if (errorMsg) {
    let alert = document.querySelector('.alert-danger');
    if (!alert) {
      alert = document.createElement('div');
      alert.className = 'alert alert-danger';
      form.insertBefore(alert, form.firstChild);
    }
    alert.textContent = errorMsg;
  }
}); 