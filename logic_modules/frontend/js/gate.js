/**
 * Lightweight beta passcode gate for static GitHub Pages.
 * Not real security — keeps casual visitors out. Passcode is hashed (SHA-256).
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'bottomline_beta_ok';
  // sha256("abdulwillbenchtovictory26")
  var PASS_HASH =
    'cdc02b447fb6cccd6e94d07bbe94ee31fe986dec6e5e936d51db64185b05c4a3';

  function unlocked() {
    try {
      return sessionStorage.getItem(STORAGE_KEY) === '1';
    } catch (e) {
      return false;
    }
  }

  function markUnlocked() {
    try {
      sessionStorage.setItem(STORAGE_KEY, '1');
    } catch (e) {
      /* private mode — still allow this session via in-memory flag */
    }
  }

  async function sha256Hex(text) {
    var data = new TextEncoder().encode(text);
    var buf = await crypto.subtle.digest('SHA-256', data);
    return Array.from(new Uint8Array(buf))
      .map(function (b) {
        return b.toString(16).padStart(2, '0');
      })
      .join('');
  }

  function injectStyles() {
    if (document.getElementById('bl-gate-css')) return;
    var style = document.createElement('style');
    style.id = 'bl-gate-css';
    style.textContent = [
      'html.bl-locked body > *:not(#bl-gate){visibility:hidden !important;}',
      '#bl-gate{visibility:visible !important;position:fixed;inset:0;z-index:99999;',
      'display:flex;align-items:center;justify-content:center;',
      'background:#121c50;color:#fcf4ed;font-family:Inter,system-ui,sans-serif;padding:1.5rem;}',
      '#bl-gate .bl-card{width:100%;max-width:380px;text-align:center;}',
      '#bl-gate .bl-brand{font-weight:800;font-size:1.35rem;letter-spacing:-0.02em;margin:0 0 0.35rem;}',
      '#bl-gate .bl-brand em{color:#d21214;font-style:normal;}',
      '#bl-gate .bl-sub{opacity:0.8;font-size:0.95rem;margin:0 0 1.5rem;line-height:1.45;}',
      '#bl-gate label{display:block;text-align:left;font-size:0.8rem;font-weight:600;margin-bottom:0.4rem;}',
      '#bl-gate input[type=password]{width:100%;box-sizing:border-box;padding:0.7em 0.85em;',
      'border:2px solid rgba(255,255,255,0.25);border-radius:8px;background:rgba(255,255,255,0.08);',
      'color:#fcf4ed;font:inherit;font-size:1rem;}',
      '#bl-gate input:focus{outline:none;border-color:#fcf4ed;}',
      '#bl-gate button{margin-top:0.9rem;width:100%;padding:0.7em 1em;border:none;border-radius:8px;',
      'background:#d21214;color:#fff;font:inherit;font-weight:700;font-size:0.95rem;cursor:pointer;}',
      '#bl-gate button:hover{filter:brightness(1.08);}',
      '#bl-gate .bl-err{color:#ffb4b4;font-size:0.85rem;min-height:1.25em;margin:0.65rem 0 0;}',
      '#bl-gate .bl-note{margin-top:1.25rem;font-size:0.75rem;opacity:0.55;}',
    ].join('');
    document.head.appendChild(style);
  }

  function showGate() {
    document.documentElement.classList.add('bl-locked');
    injectStyles();

    var root = document.getElementById('bl-gate');
    if (!root) {
      root = document.createElement('div');
      root.id = 'bl-gate';
      root.setAttribute('role', 'dialog');
      root.setAttribute('aria-modal', 'true');
      root.setAttribute('aria-labelledby', 'bl-gate-title');
      root.innerHTML =
        '<div class="bl-card">' +
        '<p class="bl-brand" id="bl-gate-title">Abdul <em>for Senate</em></p>' +
        '<p class="bl-sub">Policy Tools beta — enter the passcode to continue.</p>' +
        '<form id="bl-gate-form" autocomplete="off">' +
        '<label for="bl-gate-input">Passcode</label>' +
        '<input id="bl-gate-input" type="password" name="passcode" autocomplete="current-password" required autofocus />' +
        '<button type="submit">Enter →</button>' +
        '<p class="bl-err" id="bl-gate-err" aria-live="polite"></p>' +
        '</form>' +
        '<p class="bl-note">Private beta preview</p>' +
        '</div>';
      document.body.appendChild(root);
    }

    var form = document.getElementById('bl-gate-form');
    var input = document.getElementById('bl-gate-input');
    var err = document.getElementById('bl-gate-err');

    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      err.textContent = '';
      var value = (input.value || '').trim();
      if (!value) {
        err.textContent = 'Enter the passcode.';
        return;
      }
      try {
        var hash = await sha256Hex(value);
        if (hash !== PASS_HASH) {
          err.textContent = 'Incorrect passcode.';
          input.select();
          return;
        }
        markUnlocked();
        root.remove();
        document.documentElement.classList.remove('bl-locked');
      } catch (ex) {
        err.textContent = 'Could not verify passcode in this browser.';
      }
    });

    setTimeout(function () {
      input.focus();
    }, 0);
  }

  function boot() {
    if (unlocked()) return;
    if (document.body) showGate();
    else document.addEventListener('DOMContentLoaded', showGate);
  }

  // Hide content ASAP when locked (before body exists)
  if (!unlocked()) {
    document.documentElement.classList.add('bl-locked');
    injectStyles();
  }
  boot();
})();
