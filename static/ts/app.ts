// Пример TS: типобезопасные утилиты для работы с DOM/сообщениями

type Selector<T extends Element> = string & { __brand?: T };

const qsa = <T extends Element>(selector: Selector<T>, root: ParentNode = document): T[] =>
  Array.prototype.slice.call(root.querySelectorAll(selector));

const qs = <T extends Element>(selector: Selector<T>, root: ParentNode = document): T | null =>
  root.querySelector(selector);

function autoHideMessages(delayMs = 2500) {
  const msgs = qsa<HTMLDivElement>('.messages .msg' as Selector<HTMLDivElement>);
  if (!msgs.length) return;
  setTimeout(() => {
    msgs.forEach((el) => {
      el.style.transition = 'opacity .4s ease, transform .4s ease';
      el.style.opacity = '0';
      el.style.transform = 'translateY(-6px)';
      setTimeout(() => el.remove(), 450);
    });
  }, delayMs);
}

function preventDoubleSubmitOnVotes() {
  const forms = qsa<HTMLFormElement>('form[action*="/vote/"]' as Selector<HTMLFormElement>);
  forms.forEach((form) => {
    form.addEventListener('submit', () => {
      const btn = qs<HTMLButtonElement>('button[type="submit"]' as Selector<HTMLButtonElement>, form);
      if (btn) {
        btn.disabled = true;
        btn.classList.add('is-loading');
      }
    });
  });
}

document.addEventListener('DOMContentLoaded', () => {
  autoHideMessages();
  preventDoubleSubmitOnVotes();
});