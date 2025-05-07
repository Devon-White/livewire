/*
 * signup.js
 * Handles client-side validation and modal confirmation for the signup page (signup.html).
 */
document.getElementById('signupBtn').onclick = function(e) {
  e.preventDefault();
  let valid = true;
  ['first_name', 'last_name', 'email', 'password', 'confirm_password'].forEach(id => {
    const input = document.querySelector(`[name="${id}"]`);
    if (input && !input.value.trim()) {
      input.classList.add('is-invalid');
      valid = false;
    } else if (input) {
      input.classList.remove('is-invalid');
    }
  });
  const password = document.getElementById('password').value;
  if (password.length < 8) {
    document.getElementById('password').classList.add('is-invalid');
    document.getElementById('passwordLengthError').style.display = 'block';
    valid = false;
  } else {
    document.getElementById('password').classList.remove('is-invalid');
    document.getElementById('passwordLengthError').style.display = 'none';
  }
  const confirmPassword = document.getElementById('confirm_password').value;
  if (password !== confirmPassword) {
    document.getElementById('confirm_password').classList.add('is-invalid');
    document.getElementById('passwordMatchError').style.display = 'block';
    valid = false;
  } else {
    document.getElementById('confirm_password').classList.remove('is-invalid');
    document.getElementById('passwordMatchError').style.display = 'none';
  }
  if (valid) {
    new bootstrap.Modal(document.getElementById('confirmModal')).show();
  }
};
document.getElementById('confirmSignupBtn').onclick = function() {
  document.getElementById('signupForm').submit();
}; 