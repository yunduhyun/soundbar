document.addEventListener('DOMContentLoaded', function () {
  const bgContainer = document.querySelector('.background-image');
  const inputFields = document.querySelectorAll(
    '.input-id, .input-pw, .input-nickname',
  );

  if (bgContainer) {
    inputFields.forEach((input) => {
      input.addEventListener('focus', () => {
        bgContainer.classList.add('shaking-bg');
        input.classList.add('shaking-input');
      });
      input.addEventListener('blur', () => {
        bgContainer.classList.remove('shaking-bg');
        input.classList.remove('shaking-input');
      });
      input.addEventListener('input', () => {
        input.classList.add('bouncing-input');

        setTimeout(() => {
          input.classList.remove('bouncing-input');
        }, 100);
      });
    });
  }
});
