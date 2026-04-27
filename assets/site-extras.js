/* ============================================================
   AI DESK · site-extras.js · v1 (2026-04-27)
   Reading progress · Web Share · Save · Quote share · Search · Light mode
   ============================================================ */
(function () {
  'use strict';

  // ----------------------------------------------------------------
  // 1. Reading progress bar — 任何頁面都可掛
  // ----------------------------------------------------------------
  function initProgressBar() {
    var bar = document.createElement('div');
    bar.className = 'read-progress';
    var fill = document.createElement('div');
    fill.className = 'bar';
    bar.appendChild(fill);
    document.body.appendChild(bar);

    var ticking = false;
    function update() {
      var doc = document.documentElement;
      var scrolled = window.scrollY;
      var max = doc.scrollHeight - doc.clientHeight;
      var pct = max > 0 ? Math.min(100, Math.max(0, (scrolled / max) * 100)) : 0;
      fill.style.width = pct + '%';
      ticking = false;
    }
    window.addEventListener('scroll', function () {
      if (!ticking) {
        window.requestAnimationFrame(update);
        ticking = true;
      }
    }, { passive: true });
    update();
  }

  // ----------------------------------------------------------------
  // 2. Light / dark theme toggle (memorized in localStorage)
  // ----------------------------------------------------------------
  function initThemeToggle() {
    var saved;
    try { saved = localStorage.getItem('aidesk-theme'); } catch (e) {}
    if (saved === 'light' || saved === 'dark') {
      document.documentElement.setAttribute('data-theme', saved);
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
      // 預設仍是 dark，但尊重使用者系統偏好（如果 saved 是 null）
      // 這裡選擇預設保持品牌 dark，除非使用者主動切
    }

    var btn = document.createElement('button');
    btn.className = 'theme-toggle';
    btn.setAttribute('aria-label', 'Toggle theme');
    btn.title = 'Toggle theme (T)';
    function paint() {
      var t = document.documentElement.getAttribute('data-theme');
      btn.textContent = t === 'light' ? '◐' : '◑';
    }
    paint();
    btn.addEventListener('click', function () {
      var cur = document.documentElement.getAttribute('data-theme');
      var next = cur === 'light' ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', next);
      try { localStorage.setItem('aidesk-theme', next); } catch (e) {}
      paint();
    });
    document.body.appendChild(btn);

    document.addEventListener('keydown', function (e) {
      if (e.key === 't' && !e.metaKey && !e.ctrlKey && !e.altKey &&
          !/^(INPUT|TEXTAREA|SELECT)$/.test((e.target || {}).tagName || '')) {
        btn.click();
      }
    });
  }

  // ----------------------------------------------------------------
  // 3. Web Share API enhancement on .share-bar
  // ----------------------------------------------------------------
  function initWebShare() {
    var bars = document.querySelectorAll('.share-bar');
    if (!bars.length || !navigator.share) return;
    bars.forEach(function (bar) {
      var btn = document.createElement('button');
      btn.className = 'web-share-btn';
      btn.type = 'button';
      btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 12v7a2 2 0 002 2h12a2 2 0 002-2v-7"/><polyline points="16 6 12 2 8 6"/><line x1="12" y1="2" x2="12" y2="15"/></svg> SHARE';
      btn.addEventListener('click', function () {
        navigator.share({
          title: document.title,
          text: (document.querySelector('meta[name="description"]') || {}).content || '',
          url: location.href
        }).catch(function () {});
      });
      bar.appendChild(btn);
      bar.classList.add('web-share-ready');
    });
  }

  // ----------------------------------------------------------------
  // 4. Save buttons — disabled per Rick 2026-04-27 (用不到)
  // ----------------------------------------------------------------
  function initSaveButtons() {
    // 不再加 Pocket / Instapaper 按鈕。
    // 如果未來要加回，取消註解下面這段：
    // var bars = document.querySelectorAll('.share-bar');
    // var url = encodeURIComponent(location.href);
    // var title = encodeURIComponent(document.title);
    // bars.forEach(function (bar) { ... });
  }

  // ----------------------------------------------------------------
  // 5. Quote selection share popover (post pages)
  // ----------------------------------------------------------------
  function initQuoteShare() {
    var article = document.querySelector('article, main, .post-body');
    if (!article) return;

    var pop = document.createElement('button');
    pop.className = 'quote-popover';
    pop.type = 'button';
    pop.textContent = 'SHARE';
    document.body.appendChild(pop);

    function hide() { pop.classList.remove('show'); pop.style.display = 'none'; }

    document.addEventListener('selectionchange', function () {
      var sel = window.getSelection();
      if (!sel || sel.isCollapsed) { hide(); return; }
      var text = (sel.toString() || '').trim();
      if (text.length < 8 || text.length > 280) { hide(); return; }
      // 確認 selection 在文章內
      var node = sel.anchorNode;
      while (node && node !== article && node !== document.body) node = node.parentNode;
      if (node !== article) { hide(); return; }

      var rect = sel.getRangeAt(0).getBoundingClientRect();
      pop.style.top = (window.scrollY + rect.top - 44) + 'px';
      pop.style.left = (window.scrollX + rect.left + rect.width / 2 - 50) + 'px';
      pop.classList.add('show');
      pop.style.display = 'inline-flex';
      pop.dataset.quote = text;
    });

    pop.addEventListener('mousedown', function (e) {
      e.preventDefault();
      var quote = pop.dataset.quote || '';
      var url = location.href + '#:~:text=' + encodeURIComponent(quote.slice(0, 100));
      var shareText = '「' + quote + '」 — AI DESK';
      if (navigator.share) {
        navigator.share({ title: document.title, text: shareText, url: url }).catch(function () {});
      } else {
        // Fallback: open Twitter intent
        window.open('https://twitter.com/intent/tweet?text=' + encodeURIComponent(shareText) + '&url=' + encodeURIComponent(url), '_blank');
      }
      hide();
    });
  }

  // ----------------------------------------------------------------
  // 6. Search trigger ("/" key opens Pagefind modal)
  // ----------------------------------------------------------------
  function initSearch() {
    var modal = document.getElementById('search-modal');
    if (!modal) return;

    function open() {
      modal.classList.add('show');
      var input = modal.querySelector('input, .pagefind-ui__search-input');
      if (input) setTimeout(function () { input.focus(); }, 80);
    }
    function close() { modal.classList.remove('show'); }

    document.addEventListener('keydown', function (e) {
      if (e.key === '/' && !e.metaKey && !e.ctrlKey && !e.altKey &&
          !/^(INPUT|TEXTAREA|SELECT)$/.test((e.target || {}).tagName || '')) {
        e.preventDefault();
        open();
      } else if (e.key === 'Escape' && modal.classList.contains('show')) {
        close();
      }
    });

    var trigger = document.getElementById('search-trigger');
    if (trigger) trigger.addEventListener('click', open);

    var closeBtn = modal.querySelector('.close');
    if (closeBtn) closeBtn.addEventListener('click', close);

    modal.addEventListener('click', function (e) {
      if (e.target === modal) close();
    });
  }

  // ----------------------------------------------------------------
  // bootstrap
  // ----------------------------------------------------------------
  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }
  ready(function () {
    initThemeToggle();
    initProgressBar();
    initWebShare();
    initQuoteShare();
    initSearch();
  });
})();
