'use strict';

export function autoFadeAlerts() {
  let messages = document.getElementById('messages');
  if (messages) {
    setTimeout(() => {
      messages.remove()
    }, 5000);
  }
}

export const Messages = {
  autoFadeAlerts,
};