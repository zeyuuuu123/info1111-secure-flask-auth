(function () {
  // ------------ helpers ------------
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const debounce = (fn, ms = 250) => {
    let t; return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
  };

  // ------------ dropdown menus ------------
(function () {
  // ------------ helpers ------------
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const debounce = (fn, ms = 250) => {
    let t; return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
  };

  // ------------ dropdown menus ------------
  function closeAllMenus(except) {
    $$('.menu').forEach(m => { if (m !== except) m.classList.remove('open'); });
  }

  // Toggle open/close on buttons
  $$('.menu .menu-toggle').forEach(btn => {
    const menu = btn.closest('.menu');
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      const isOpen = menu.classList.contains('open');
      closeAllMenus(menu);
      if (!isOpen) {
        menu.classList.add('open');
        // If this is the user menu with a login form, autofocus username
        const firstInput = menu.querySelector('.dropdown-menu input, .dropdown-menu select, .dropdown-menu textarea');
        if (firstInput) setTimeout(() => firstInput.focus(), 0);
      } else {
        menu.classList.remove('open');
      }
    });

    // Optional: open on keyboard (Enter/Space)
    btn.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        btn.click();
      }
    });
  });

  // Prevent clicks *inside* any dropdown from bubbling to document
  $$('.menu .dropdown-menu').forEach(panel => {
    panel.addEventListener('click', (e) => {
      e.stopPropagation();
    });
    panel.addEventListener('mousedown', (e) => {
      // Prevent focus loss on inputs due to mousedown bubbling
      e.stopPropagation();
    });
  });

  // Close menus when clicking outside any .menu
  document.addEventListener('click', (e) => {
    const insideMenu = e.target.closest('.menu');
    if (!insideMenu) closeAllMenus(null);
  });

  // Close on Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeAllMenus(null);
  });

  // ------------ live profile search ------------
  const input = $('#profile-search');
  const resultsBox = $('#search-results');
  if (input && resultsBox) {
    const renderResults = (items) => {
      if (!items || items.length === 0) {
        resultsBox.innerHTML = '<div class="result-item"><em>No results</em></div>';
        resultsBox.hidden = false;
        return;
      }
      resultsBox.innerHTML = items.map(it => {
        const classes = (it.classes || []).join(', ');
        const q = encodeURIComponent(it.username || it.name || '');
        return `
          <div class="result-item">
            <a href="/profiles/search?query=${q}">
              <div><strong>${(it.name || it.username)}</strong> <span class="result-secondary">(${it.username})</span></div>
              <div class="result-secondary">${classes}</div>
            </a>
          </div>
        `;
      }).join('');
      resultsBox.hidden = false;
    };

    const doSearch = debounce(async () => {
      const q = input.value.trim();
      if (!q) { resultsBox.hidden = true; resultsBox.innerHTML = ''; return; }
      try {
        const r = await fetch(`/profiles/search?query=${encodeURIComponent(q)}&format=json`);
        if (!r.ok) throw new Error('search failed');
        const data = await r.json();
        renderResults((data && data.results) || []);
      } catch (e) {
        resultsBox.innerHTML = '<div class="result-item"><em>Error searching</em></div>';
        resultsBox.hidden = false;
      }
    }, 250);

    input.addEventListener('input', doSearch);
    input.addEventListener('focus', () => { if (resultsBox.innerHTML) resultsBox.hidden = false; });

    // Keep search results open when clicking inside
    if (resultsBox) {
      resultsBox.addEventListener('mousedown', (e) => e.stopPropagation());
      resultsBox.addEventListener('click', (e) => e.stopPropagation());
    }

    // Close results when clicking outside
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.search')) {
        resultsBox.hidden = true;
      }
    });
  }
})();
  // ------------ live profile search ------------
  const input = $('#profile-search');
  const resultsBox = $('#search-results');
  if (input && resultsBox) {
    const renderResults = (items) => {
      if (!items || items.length === 0) {
        resultsBox.innerHTML = '<div class="result-item"><em>No results</em></div>';
        resultsBox.hidden = false;
        return;
        }
      resultsBox.innerHTML = items.map(it => {
        const classes = (it.classes || []).join(', ');
        // Link to full search page (HTML results), using name for clarity
        const q = encodeURIComponent(it.username || it.name || '');
        return `
          <div class="result-item">
            <a href="/profiles/search?query=${q}">
              <div><strong>${(it.name || it.username)}</strong> <span class="result-secondary">(${it.username})</span></div>
              <div class="result-secondary">${classes}</div>
            </a>
          </div>
        `;
      }).join('');
      resultsBox.hidden = false;
    };

    const doSearch = debounce(async () => {
      const q = input.value.trim();
      if (!q) { resultsBox.hidden = true; resultsBox.innerHTML = ''; return; }
      try {
        const r = await fetch(`/profiles/search?query=${encodeURIComponent(q)}&format=json`);
        if (!r.ok) throw new Error('search failed');
        const data = await r.json();
        renderResults((data && data.results) || []);
      } catch (e) {
        resultsBox.innerHTML = '<div class="result-item"><em>Error searching</em></div>';
        resultsBox.hidden = false;
      }
    }, 250);

    input.addEventListener('input', doSearch);
    input.addEventListener('focus', () => { if (resultsBox.innerHTML) resultsBox.hidden = false; });
    document.addEventListener('click', (e) => {
      if (!resultsBox.contains(e.target) && e.target !== input) {
        resultsBox.hidden = true;
      }
    });
  }
})();