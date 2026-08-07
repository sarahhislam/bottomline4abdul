document.addEventListener('DOMContentLoaded', () => {
  // Smooth scroll for same-page anchors
  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener('click', (e) => {
      e.preventDefault();
      const id = a.getAttribute('href').slice(1);
      const el = document.getElementById(id);
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    });
  });

  // Wire data-module-run buttons to client-side modules (GitHub Pages–safe)
  document.querySelectorAll('[data-module-run]').forEach((btn) => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();

      const moduleName = btn.getAttribute('data-module-run');
      const outputSel = btn.getAttribute('data-output');
      const outputEl = outputSel ? document.querySelector(outputSel) : null;
      if (!outputEl) return;

      const form = btn.closest('[data-module-form]') || btn.closest('.tool-body') || document;
      const params = {};
      form.querySelectorAll('input[name], select[name], textarea[name]').forEach((el) => {
        if (el.name) params[el.name] = el.value;
      });

      outputEl.textContent = 'Running…';
      btn.setAttribute('aria-busy', 'true');

      try {
        if (!window.BottomlineModules) {
          throw new Error('Module runtime not loaded. Check that modules.js is included.');
        }
        const result = await window.BottomlineModules.run(moduleName, params);
        outputEl.textContent = result;
      } catch (err) {
        outputEl.textContent = `Error: ${err.message || err}`;
      } finally {
        btn.removeAttribute('aria-busy');
      }
    });
  });
});
