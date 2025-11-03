(function () {
  const out = {
    root: document.getElementById('section-output'),
    title: document.getElementById('output-title'),
    text: document.getElementById('output-text')
  };

  function show(title, text) {
    out.title.textContent = title;
    out.text.textContent = text;
    out.root.hidden = false;
  }

  function initButtons() {
    document.querySelectorAll('.btn').forEach((btn) => {
      btn.addEventListener('click', async () => {
        const action = btn.dataset.action;
        if (action === 'mission') {
          show('Миссия', 'Помочь молодежи и студентам СПО развить навыки для построения карьеры мечты или открытия собственного дела через практико-ориентированный подход.');
        } else if (action === 'program') {
          show('Программа', 'Адаптация, развитие soft skills, стажировки, лидерство и реальная практика на проектах.');
        } else if (action === 'register') {
          try {
            if (window.vkBridge) {
              await vkBridge.send('VKWebAppOpenApp', { app_id: 0 });
            }
          } catch (e) {}
          show('Регистрация', 'Регистрация будет доступна в рамках мини-приложения.');
        }
      });
    });
  }

  document.addEventListener('DOMContentLoaded', initButtons);
})();


