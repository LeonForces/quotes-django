(function () {
  'use strict';

  // Автоскрытие flash-сообщений
  function autoHideMessages() {
    var msgs = document.querySelectorAll('.messages .msg');
    if (!msgs.length) return;
    setTimeout(function () {
      msgs.forEach(function (el) {
        el.style.transition = 'opacity .4s ease, transform .4s ease';
        el.style.opacity = '0';
        el.style.transform = 'translateY(-6px)';
        setTimeout(function () {
          if (el && el.parentNode) el.parentNode.removeChild(el);
        }, 450);
      });
    }, 2500);
  }

  // Защита от двойной отправки голосов
  function preventDoubleSubmitOnVotes() {
    var voteForms = document.querySelectorAll('form[action*="/vote/"]');
    voteForms.forEach(function (form) {
      form.addEventListener('submit', function () {
        var btn = form.querySelector('button[type="submit"]');
        if (btn) {
          btn.disabled = true;
          btn.classList.add('is-loading');
        }
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    autoHideMessages();
    preventDoubleSubmitOnVotes();
  });
})();