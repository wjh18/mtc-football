'use strict';

export function createAlert(message, type) {
  let alert = document.createElement('div');
  alert.classList.add("alert", `alert-${type}`);
  alert.setAttribute("role", "alert");
  alert.innerHTML = `<span>${message}</span><button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`
  fadeAlert(alert);
  document.getElementById('messages').appendChild(alert);
}

function autoFadeAlerts() {
  const messages = document.querySelectorAll(".alert");
  for (const alert of messages) {
    fadeAlert(alert);
    const btn = alert.querySelector(".btn-close")
    btn.addEventListener('click', function() {
      alert.remove();
    });
  }
}

function fadeAlert(alert) {
  setTimeout(() => {
    alert.remove()
  }, 5000);
}

export const Messages = {
  createAlert,
  autoFadeAlerts,
};