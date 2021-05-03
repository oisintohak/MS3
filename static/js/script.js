// flash message popup/close
const closeFlashedMessages = document.querySelector('#close-flashed-messages');
const flashedMessages = document.querySelector('#flashed-messages');
if (flashedMessages != null) {
  closeFlashedMessages.addEventListener('click', () => {
    flashedMessages.classList.add('is-hidden');
  });
}

// file size and extension validation
const fileUpload = document.querySelector('#image');
if (fileUpload != null) {
  fileUpload.addEventListener('change', function validate (event) {
    const files = event.target.files;
    const display = document.querySelector('#filesize-validation');
    const submit = document.querySelector('#submit-button');
    if (files.length > 0) {
      if (validFileType(files[0])) {
        if (Math.round(files[0].size / 1024) < 2048) {
          display.innerHTML = '';
          submit.disabled = false;
        }
        else {
          display.innerHTML = 'Maximum file size is 2MB. Please choose a smaller file';
          submit.disabled = true;
        }
      }
      else {
        display.innerHTML = 'Only .jpg, .jpeg or .png extensions are allowed';
        submit.disabled = true;      
    }
  }
});
}

// code taken from https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/file
const fileTypes = [
  "image/jpeg",
  "image/pjpeg",
  "image/jpg",
  "image/png",
];

function validFileType(file) {
  return fileTypes.includes(file.type);
}
