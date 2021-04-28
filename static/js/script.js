const closeFlashedMessages = document.querySelector('#close-flashed-messages');
const flashedMessages = document.querySelector('#flashed-messages');
if (flashedMessages != null) {
  closeFlashedMessages.addEventListener('click', () => {
    flashedMessages.classList.add('is-hidden');
  });
}