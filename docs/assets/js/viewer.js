/* oversightengineering.com — proof viewer.
 *
 * Certificate and letter proofs open in place, on top of the page, with a Back button
 * and a Close button. Nothing navigates the reader away from the record they were
 * reading. Third-party pages and PDFs are not intercepted: they open in their own tab,
 * so the reader closes the tab and is back where they started.
 *
 * The link's href still points at the file, so the proof opens on its own if this
 * script never runs.
 */
(function () {
  'use strict';

  var dlg = null;
  var titleEl = null;
  var imgEl = null;
  var openA = null;
  var lastTrigger = null;
  var IMAGE = /\.(png|jpe?g|webp|gif|svg)$/i;

  function build() {
    dlg = document.createElement('div');
    dlg.className = 'viewer';
    dlg.hidden = true;
    dlg.setAttribute('role', 'dialog');
    dlg.setAttribute('aria-modal', 'true');
    dlg.setAttribute('aria-labelledby', 'viewer-title');
    dlg.innerHTML =
      '<div class="viewer-bar">' +
        '<p class="viewer-title" id="viewer-title"></p>' +
        '<div class="viewer-acts">' +
          '<a class="viewer-btn" data-act="file" target="_blank" rel="noopener noreferrer">Open image</a>' +
          '<button class="viewer-btn" type="button" data-act="back">\u2190 Back</button>' +
          '<button class="viewer-btn viewer-x" type="button" data-act="close" aria-label="Close">\u00d7</button>' +
        '</div>' +
      '</div>' +
      '<div class="viewer-stage"><img alt=""></div>';
    document.body.appendChild(dlg);
    titleEl = dlg.querySelector('.viewer-title');
    imgEl = dlg.querySelector('img');
    openA = dlg.querySelector('[data-act="file"]');
    dlg.addEventListener('click', onClick);
    document.addEventListener('keydown', onKey);
  }

  function show(trigger, src, title) {
    if (!dlg) build();
    lastTrigger = trigger;
    titleEl.textContent = title || 'Proof';
    imgEl.src = src;
    imgEl.alt = title || 'Proof document';
    openA.href = src;
    dlg.hidden = false;
    document.body.classList.add('viewer-open');
    if (!(history.state && history.state.viewer)) {
      history.pushState({ viewer: true }, '', location.pathname + location.search + '#proof');
    }
    dlg.querySelector('[data-act="back"]').focus();
  }

  function hide() {
    if (!dlg || dlg.hidden) return;
    dlg.hidden = true;
    document.body.classList.remove('viewer-open');
    imgEl.removeAttribute('src');
    if (lastTrigger && lastTrigger.focus) lastTrigger.focus();
    lastTrigger = null;
    if (history.state && history.state.viewer) {
      history.replaceState(null, '', location.pathname + location.search);
    }
  }

  /* Back means back: it takes the reader out of the viewer the same way the browser
     back button would, so the two behave identically. */
  function goBack() {
    if (history.state && history.state.viewer) {
      history.back();
    } else {
      hide();
    }
  }

  function onClick(e) {
    var btn = e.target.closest ? e.target.closest('[data-act]') : null;
    if (btn) {
      var act = btn.getAttribute('data-act');
      if (act === 'close') hide();
      else if (act === 'back') goBack();
      return;
    }
    if (e.target.classList && e.target.classList.contains('viewer-stage')) goBack();
  }

  function onKey(e) {
    if (!dlg || dlg.hidden) return;
    if (e.key === 'Escape') {
      e.preventDefault();
      goBack();
      return;
    }
    if (e.key === 'Tab') {
      var f = dlg.querySelectorAll('a[href], button');
      var first = f[0];
      var last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest ? e.target.closest('a.proof') : null;
    if (!a) return;
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
    var src = a.getAttribute('data-proof') || a.getAttribute('href');
    if (!src || !IMAGE.test(src)) return;
    e.preventDefault();
    show(a, src, a.getAttribute('data-title') || a.textContent.replace(/\s+/g, ' ').trim());
  });

  window.addEventListener('popstate', function () {
    if (dlg && !dlg.hidden) hide();
  });
})();
