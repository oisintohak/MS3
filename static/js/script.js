const closeFlashedMessages = document.querySelector('#close-flashed-messages');
const flashedMessages = document.querySelector('#flashed-messages');
closeFlashedMessages.addEventListener('click', () => {
  flashedMessages.classList.add('is-hidden');
});