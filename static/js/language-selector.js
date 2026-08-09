/**
 * ============================================================
 * ABDUL FOR SENATE — GLOBAL LANGUAGE SELECTOR
 * ============================================================
 *
 * This script provides a prominent, modern language dropdown
 * that appears in the top-right of every page. It supports
 * 13 languages and translates the page DOM content.
 *
 * TRANSLATION ARCHITECTURE:
 *   1. PRIMARY — Custom Flask backend: POST /api/translate
 *      (web_app.py + translator.py, deep-translator w/ cache).
 *      The visible text nodes of <body> are collected and
 *      batch-translated, then written back into the DOM.
 *   2. FALLBACK — Google Translate widget (only used when the
 *      backend API is not reachable, e.g. static GitHub Pages).
 *
 * HOW TO ADD/REMOVE A LANGUAGE:
 *   Edit the LANGUAGES array below. Each entry has:
 *     - code:   Translation language code (must be accepted by
 *               /api/translate OR Google Translate)
 *     - name:   English display name shown in the dropdown
 *     - native: Native script name shown alongside English
 *     - flag:   Emoji flag for visual identification
 *
 * HOW TO CHANGE THE DEFAULT LANGUAGE:
 *   Edit the DEFAULT_LANG constant below.
 * ============================================================
 */

// ─── Supported Languages (Dual-Language Display) ───
const LANGUAGES = [
  { code: 'en',    name: 'English',    native: 'English',    flag: '🇺🇸' },
  { code: 'hi',    name: 'Hindi',      native: 'हिन्दी',      flag: '🇮🇳' },
  { code: 'ar',    name: 'Arabic',     native: 'العربية',     flag: '🇸🇦' },
  { code: 'ur',    name: 'Urdu',       native: 'اردو',       flag: '🇵🇰' },
  { code: 'es',    name: 'Spanish',    native: 'Español',    flag: '🇪🇸' },
  { code: 'bn',    name: 'Bangla',     native: 'বাংলা',      flag: '🇧🇩' },
  { code: 'iw',    name: 'Hebrew',     native: 'עברית',      flag: '🇵🇸' },
  { code: 'fa',    name: 'Farsi',      native: 'فارسی',      flag: '🇮🇷' },
  { code: 'it',    name: 'Italian',    native: 'Italiano',   flag: '🇮🇹' },
  { code: 'pl',    name: 'Polish',     native: 'Polski',     flag: '🇵🇱' },
  { code: 'zh-CN', name: 'Chinese',    native: '中文',       flag: '🇨🇳' },
  { code: 'ja',    name: 'Japanese',   native: '日本語',     flag: '🇯🇵' },
  { code: 'ko',    name: 'Korean',     native: '한국어',     flag: '🇰🇷' }
];

// ─── Default Language ───
const DEFAULT_LANG = 'en';

// ─── RTL Languages ───
const RTL_LANGS = ['ar', 'ur', 'fa', 'iw'];

// ─── Elements / text that must never be translated ───
const SKIP_SELECTOR =
  'script, style, noscript, template, pre, code, textarea, select, ' +
  'input, [contenteditable="true"], #lang-selector-wrap, ' +
  '.translate-widget-container, .goog-te-banner-frame iframe';

// Patterns that are never worth translating (numbers, URLs, emails,
// currency amounts, pure symbols, etc.)
function isTranslatableText(text) {
  const t = text.trim();
  if (!t) return false;
  if (t.length <= 2) return false;
  // Only digits / punctuation / symbols / spaces?
  if (/^[\d\s.,$%#@&*()+\-=_/\\|:;'"<>!?~^\[\]{}`]+$/.test(t)) return false;
  // URLs / emails / file paths
  if (/^(https?:\/\/|www\.|mailto:|\.\.?\/|\/pages\/)/i.test(t)) return false;
  // Pure numbers or numeric ranges like "$500"
  if (/^[$€£]\s?[\d,.]+$/.test(t)) return false;
  return true;
}

// ─── Track original (English) text so we can restore / re-translate ───
const _origTextNode = new WeakMap();   // TextNode  → original string
const _origPlaceholder = new WeakMap(); // Element   → original placeholder

function getSourceText(node) {
  if (_origTextNode.has(node)) return _origTextNode.get(node);
  return node.data;
}

function getSourcePlaceholder(el) {
  if (_origPlaceholder.has(el)) return _origPlaceholder.get(el);
  return el.getAttribute('placeholder') || '';
}

// ─── API base detection (works from / and from /pages/…) ───
function apiBase() {
  const scripts = document.querySelectorAll('script[src]');
  for (const s of scripts) {
    if (s.src && s.src.indexOf('language-selector.js') !== -1) {
      return s.src.replace(/js\/language-selector\.js(\?.*)?$/, '');
    }
  }
  return './';
}

function apiUrl(relativePath) {
  return apiBase() + relativePath.replace(/^\//, '');
}

// ─── Collect eligible text nodes under <body> ───
function collectTextNodes(root) {
  const nodes = [];
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      const parent = node.parentElement;
      if (!parent) return NodeFilter.FILTER_REJECT;
      if (parent.closest(SKIP_SELECTOR)) return NodeFilter.FILTER_REJECT;
      if (!isTranslatableText(node.data)) return NodeFilter.FILTER_REJECT;
      return NodeFilter.FILTER_ACCEPT;
    }
  });
  let n;
  while ((n = walker.nextNode())) nodes.push(n);
  return nodes;
}

// ─── Collect eligible placeholder elements ───
function collectPlaceholders(root) {
  const els = [];
  root.querySelectorAll('input[placeholder], textarea[placeholder]').forEach((el) => {
    if (el.closest(SKIP_SELECTOR)) return;
    const ph = el.getAttribute('placeholder') || '';
    if (isTranslatableText(ph)) els.push(el);
  });
  return els;
}

// ─── Primary path: translate through the custom backend API ───
async function translateViaApi(code) {
  // Build de-duplicated batch from originals (English) so
  // switching ar → hi always translates from English, not Arabic.
  const textNodes = collectTextNodes(document.body);
  const placeholders = collectPlaceholders(document.body);

  const ordered = [];            // [{type:'node', node}|{type:'ph', el}]
  const byText = new Map();      // source text → index into ordered

  function pushEntry(entry, text) {
    if (!isTranslatableText(text)) return;
    if (byText.has(text)) return; // already in batch — reuse translation
    byText.set(text, ordered.length);
    ordered.push(entry);
  }

  textNodes.forEach((node) => pushEntry({ type: 'node', node }, getSourceText(node)));
  placeholders.forEach((el) => pushEntry({ type: 'ph', el }, getSourcePlaceholder(el)));

  if (ordered.length === 0) return;

  const texts = ordered.map((entry) =>
    entry.type === 'node' ? getSourceText(entry.node) : getSourcePlaceholder(entry.el)
  );

  const res = await fetch(apiUrl('api/translate'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ texts: texts, target: code })
  });

  if (!res.ok) {
    const errText = await res.text().catch(() => '');
    throw new Error('API ' + res.status + ': ' + errText.slice(0, 120));
  }

  const data = await res.json();
  if (!data.translations || data.translations.length !== texts.length) {
    throw new Error('Unexpected API response shape');
  }

  // Store originals on first translation, then apply translations
  ordered.forEach((entry, i) => {
    const translated = data.translations[i];
    if (translated == null) return;
    if (entry.type === 'node') {
      if (!_origTextNode.has(entry.node)) {
        _origTextNode.set(entry.node, entry.node.data);
      }
      entry.node.data = translated;
    } else {
      if (!_origPlaceholder.has(entry.el)) {
        _origPlaceholder.set(entry.el, entry.el.getAttribute('placeholder') || '');
      }
      entry.el.setAttribute('placeholder', translated);
    }
  });
}

// ─── Fallback path: Google Translate widget (static hosting) ───
function triggerGoogleTranslate(code) {
  if (typeof google === 'undefined' || !google.translate) return;

  // The widget may have rendered a <select class="goog-te-combo"> —
  // drive it directly when present.
  const select = document.querySelector('.goog-te-combo');
  if (select) {
    select.value = code;
    select.dispatchEvent(new Event('change', { bubbles: true }));
    return;
  }

  // Otherwise, request a reload so the widget re-renders (some layouts
  // generate the combo only after interaction).
  if (google.translate.TranslateElement && google.translate.TranslateElement.reload) {
    try { google.translate.TranslateElement.reload(); } catch (e) { /* noop */ }
  }
}

// ─── Restore English from stored originals ───
function restoreEnglish() {
  const restoreNodes = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      if (_origTextNode.has(node)) return NodeFilter.FILTER_ACCEPT;
      return NodeFilter.FILTER_SKIP;
    }
  });
  let n;
  while ((n = walker.nextNode())) restoreNodes.push(n);

  restoreNodes.forEach((node) => {
    if (_origTextNode.has(node)) node.data = _origTextNode.get(node);
  });

  document.querySelectorAll('input[placeholder], textarea[placeholder]').forEach((el) => {
    if (_origPlaceholder.has(el)) {
      el.setAttribute('placeholder', _origPlaceholder.get(el));
    }
  });
}

// ─── Select a language and trigger translation ───
async function selectLanguage(code, name) {
  // Update the button text
  const btnText = document.getElementById('lang-btn-text');
  if (btnText) btnText.textContent = name;

  // Save preference to localStorage
  try {
    localStorage.setItem('abdul_lang', code);
  } catch (e) { /* ignore */ }

  // Update <html lang> + direction immediately
  document.documentElement.setAttribute('lang', code);
  document.documentElement.setAttribute('dir', RTL_LANGS.indexOf(code) !== -1 ? 'rtl' : 'ltr');

  // Show subtle "Translating…" state
  const btn = document.getElementById('lang-btn');
  if (btn) btn.setAttribute('aria-busy', 'true');

  try {
    if (code === 'en') {
      // Restore the original English content
      restoreEnglish();
      triggerGoogleTranslate('en'); // ensure Google widget resets too
    } else {
      try {
        // PRIMARY: custom backend translation API
        await translateViaApi(code);
      } catch (apiErr) {
        // FALLBACK: Google Translate widget (static GitHub Pages)
        triggerGoogleTranslate(code);
      }
    }
  } finally {
    if (btn) btn.removeAttribute('aria-busy');
  }
}

// ─── Build the language selector UI ───
function buildLanguageSelector() {
  const container = document.getElementById('lang-selector-wrap');
  if (!container) return;

  // Main button
  const btn = document.createElement('button');
  btn.id = 'lang-btn';
  btn.setAttribute('aria-label', 'Select language');
  btn.setAttribute('aria-haspopup', 'true');
  btn.setAttribute('aria-expanded', 'false');
  btn.innerHTML =
    '<span class="lang-globe">🌐</span> ' +
    '<span class="lang-btn-text" id="lang-btn-text">English</span> ' +
    '<span class="lang-arrow">▾</span>';

  // Dropdown
  const dropdown = document.createElement('div');
  dropdown.id = 'lang-dropdown';
  dropdown.setAttribute('role', 'menu');

  LANGUAGES.forEach(function (lang) {
    const link = document.createElement('a');
    link.href = '#';
    link.setAttribute('data-lang', lang.code);
    link.setAttribute('role', 'menuitem');
    link.innerHTML =
      '<span class="lang-flag">' + lang.flag + '</span>' +
      '<span class="lang-native">' + lang.native + '</span>' +
      '<span class="lang-name">' + lang.name + '</span>';
    link.addEventListener('click', function (e) {
      e.preventDefault();
      selectLanguage(lang.code, lang.name);
      closeDropdown();
    });
    dropdown.appendChild(link);
  });

  container.appendChild(btn);
  container.appendChild(dropdown);

  btn.addEventListener('click', function (e) {
    e.stopPropagation();
    const isOpen = dropdown.style.display === 'block';
    closeDropdown();
    if (!isOpen) {
      dropdown.style.display = 'block';
      btn.setAttribute('aria-expanded', 'true');
    }
  });

  document.addEventListener('click', function (e) {
    if (!container.contains(e.target)) closeDropdown();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeDropdown();
  });

  function closeDropdown() {
    dropdown.style.display = 'none';
    btn.setAttribute('aria-expanded', 'false');
  }
}

// ─── Initialize on DOM ready ───
document.addEventListener('DOMContentLoaded', function () {
  buildLanguageSelector();

  // Restore saved language preference
  try {
    const saved = localStorage.getItem('abdul_lang');
    if (saved && saved !== DEFAULT_LANG) {
      const lang = LANGUAGES.find(function (l) { return l.code === saved; });
      if (lang) selectLanguage(lang.code, lang.name);
    }
  } catch (e) { /* ignore */ }
});