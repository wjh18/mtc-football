'use strict';

function autoFadeAlerts() {
  let messages = document.getElementById('messages');
  if (messages) {
    setTimeout(() => {
      messages.remove()
    }, 5000);
  }
}

const Messages = (() => {
  autoFadeAlerts();
})();

export default Messages;