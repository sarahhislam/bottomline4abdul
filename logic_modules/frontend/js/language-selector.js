/**
 * ============================================================
 * ABDUL FOR SENATE — GLOBAL LANGUAGE SELECTOR
 * ============================================================
 * 
 * This script provides a prominent, modern language dropdown
 * that appears in the top-right of every page. It supports
 * 13 languages and triggers instant DOM translation via the
 * Google Translate widget.
 * 
 * HOW TO ADD/REMOVE A LANGUAGE:
 *   Edit the LANGUAGES array below. Each entry has:
 *     - code:   Google Translate language code
 *     - name:   English display name shown in the dropdown
 *     - native: Native script name shown alongside English
 *     - flag:   Emoji flag for visual identification
 * 
 * HOW TO CHANGE THE DEFAULT LANGUAGE:
 *   Edit the DEFAULT_LANG constant below.
 * ============================================================
 */

// ─── Supported Languages (Dual-Language Display) ───
// Each language shows BOTH its native script and English name.
// Add or remove languages here. The Google Translate widget
// will automatically pick up the includedLanguages list.
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
const DEFAULT_LANG = 'enhi';

// ─── Build the language selector UI ───
function buildLanguageSelector() {
  // Find the container element
  const container = document.getElementById('lang-selector-wrap');
  if (!container) return;

  // Create the main button (large, prominent, globe icon)
  const btn = document.createElement('button');
  btn.id = 'lang-btn';
  btn.setAttribute('aria-label', 'Select language');
  btn.setAttribute('aria-haspopup', 'true');
  btn.setAttribute('aria-expanded', 'false');
  btn.innerHTML = '<span class="lang-globe">🌐</span> <span class="lang-btn-text" id="lang-btn-text">English</span> <span class="lang-arrow">▾</span>';

  // Create the dropdown
  const dropdown = document.createElement('div');
  dropdown.id = 'lang-dropdown';
  dropdown.setAttribute('role', 'menu');

  // Populate dropdown with dual-language options
  LANGUAGES.forEach(function(lang) {
    const link = document.createElement('a');
    link.href = '#';
    link.setAttribute('data-lang', lang.code);
    link.setAttribute('role', 'menuitem');
    link.innerHTML =
      '<span class="lang-flag">' + lang.flag + '</span>' +
      '<span class="lang-native">' + lang.native + '</span>' +
      '<span class="lang-name">' + lang.name + '</span>';
    link.addEventListener('click', function(e) {
      e.preventDefault();
      selectLanguage(lang.code, lang.name);
      closeDropdown();
    });
    dropdown.appendChild(link);
  });

  // Append to container
  container.appendChild(btn);
  container.appendChild(dropdown);

  // Toggle dropdown on button click
  btn.addEventListener('click', function(e) {
    e.stopPropagation();
    const isOpen = dropdown.style.display === 'block';
    closeDropdown();
    if (!isOpen) {
      dropdown.style.display = 'block';
      btn.setAttribute('aria-expanded', 'true');
    }
  });

  // Close dropdown when clicking outside
  document.addEventListener('click', function(e) {
    if (!container.contains(e.target)) {
      closeDropdown();
    }
  });

  // Close dropdown on Escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeDropdown();
  });

  function closeDropdown() {
    dropdown.style.display = 'none';
    btn.setAttribute('aria-expanded', 'false');
  }
}

// ─── Select a language and trigger translation ───
function selectLanguage(code, name) {
  // Update the button text
  const btnText = document.getElementById('lang-btn-text');
  if (btnText) btnText.textContent = name;

  // Save preference to localStorage
  try {
    localStorage.setItem('abdul_lang', code);
  } catch (e) { /* ignore */ }

  // Trigger Google Translate
  if (typeof google !== 'undefined' && google.translate) {
    const select = document.querySelector('.goog-te-combo');
    if (select) {
      select.value = code;
      select.dispatchEvent(new Event('change'));
    }
  }

  // Set RTL direction for RTL languages
  const rtlLangs = ['ar', 'ur', 'fa', 'iw'];
  if (rtlLangs.includes(code)) {
    document.documentElement.setAttribute('dir', 'rtl');
  } else {
    document.documentElement.setAttribute('dir', 'ltr');
  }
}

// ─── Initialize on DOM ready ───
document.addEventListener('DOMContentLoaded', function() {
  buildLanguageSelector();

  // Restore saved language preference
  try {
    const saved = localStorage.getItem('abdul_lang');
    if (saved && saved !== DEFAULT_LANG) {
      const lang = LANGUAGES.find(function(l) { return l.code === saved; });
      if (lang) selectLanguage(lang.code, lang.name);
    }
  } catch (e) { /* ignore */ }
});