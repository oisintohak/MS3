document.querySelector('#image').addEventListener('change', (event) => {
  const files = event.target.files;
  const display = document.querySelector('#filesize-validation');
  const submit = document.querySelector('#submit-button');
  if (files.length > 0) {
    if (Math.round(files[0].size / 1024) > 2048) {
      display.innerHTML = 'Maximum file size is 2MB. Please choose a smaller file';
      submit.disabled = true;
    }
    else {
      display.innerHTML = '';
      submit.disabled = false;
    }
  }
});